"""
Chat History Service

Handles persistence of chat messages to/from Firestore.
Ensures all chat history is saved and can be retrieved across sessions.
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from google.cloud import firestore

logger = logging.getLogger(__name__)


class ChatHistoryService:
    """
    Service for managing chat history persistence in Firestore.
    
    Collections:
    - chat_messages: Individual messages
    - chat_threads: Thread metadata
    """
    
    def __init__(self, firestore_client: firestore.Client):
        self.firestore = firestore_client
    
    async def save_message(
        self,
        thread_id: str,
        user_id: str,
        role: str,  # 'user' | 'assistant' | 'tool_call' | 'tool_result' | 'agent_status' | 'system'
        content: str,
        message_id: Optional[str] = None,
        agent: Optional[str] = None,
        tool_args: Optional[Dict[str, Any]] = None,
        tool_call_id: Optional[str] = None,
        node: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save a chat message to Firestore.
        
        Args:
            thread_id: Thread/conversation ID
            user_id: User ID
            role: Message role
            content: Message content
            message_id: Optional specific message ID (generates if not provided)
            agent: Agent/tool name
            tool_args: Tool arguments (for tool_call messages)
            tool_call_id: Tool call ID (for linking call → result)
            node: Graph node name
            metadata: Additional metadata
            
        Returns:
            message_id: The saved message ID
        """
        try:
            # Create message document
            message_data = {
                'thread_id': thread_id,
                'user_id': user_id,
                'role': role,
                'content': content,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Add optional fields
            if agent:
                message_data['agent'] = agent
            if tool_args:
                message_data['tool_args'] = tool_args
            if tool_call_id:
                message_data['tool_call_id'] = tool_call_id
            if node:
                message_data['node'] = node
            if metadata:
                message_data['metadata'] = metadata
            
            # Save to Firestore
            if message_id:
                # Use provided ID
                self.firestore.collection('chat_messages').document(message_id).set(message_data)
            else:
                # Generate new ID
                doc_ref = self.firestore.collection('chat_messages').add(message_data)
                message_id = doc_ref[1].id
            
            # Update thread last activity
            await self._update_thread_activity(thread_id, user_id)
            
            logger.debug(f"Saved message {message_id} to thread {thread_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            raise
    
    async def get_thread_messages(
        self,
        thread_id: str,
        user_id: str,
        # limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve messages for a thread.
        
        Args:
            thread_id: Thread ID
            user_id: User ID (for security)
            limit: Maximum messages to retrieve
            
        Returns:
            List of message dicts, ordered by timestamp (oldest first)
        """
        try:
            # Query without order_by to avoid requiring Firestore composite index
            # We'll sort in Python instead
            messages_ref = (
                self.firestore.collection('chat_messages')
                .where('thread_id', '==', thread_id)
                .where('user_id', '==', user_id)
            )
            
            docs = messages_ref.stream()
            messages = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                messages.append(data)
            
            # Sort by created_at in Python
            messages.sort(key=lambda x: x.get('created_at', ''))
            
            logger.info(f"Retrieved {len(messages)} messages for thread {thread_id}")
            return messages
            
        except Exception as e:
            logger.error(f"Failed to retrieve messages: {e}")
            return []
    
    async def get_user_threads(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get all threads for a user, ordered by last activity.
        
        Args:
            user_id: User ID
            limit: Maximum threads to retrieve
            
        Returns:
            List of thread metadata dicts
        """
        try:
            threads_ref = (
                self.firestore.collection('chat_threads')
                .where('user_id', '==', user_id)
                .order_by('last_activity', direction=firestore.Query.DESCENDING)
                .limit(limit)
            )
            
            docs = threads_ref.stream()
            threads = []
            
            for doc in docs:
                data = doc.to_dict()
                data['thread_id'] = doc.id
                threads.append(data)
            
            return threads
            
        except Exception as e:
            logger.error(f"Failed to retrieve threads: {e}")
            return []
    
    async def clear_thread(
        self,
        thread_id: str,
        user_id: str
    ) -> int:
        """
        Clear all messages in a thread.
        
        Args:
            thread_id: Thread ID to clear
            user_id: User ID (for security)
            
        Returns:
            Number of messages deleted
        """
        try:
            messages_ref = (
                self.firestore.collection('chat_messages')
                .where('thread_id', '==', thread_id)
                .where('user_id', '==', user_id)
            )
            
            docs = messages_ref.stream()
            deleted_count = 0
            
            # Delete in batches
            batch = self.firestore.batch()
            batch_count = 0
            
            for doc in docs:
                batch.delete(doc.reference)
                batch_count += 1
                deleted_count += 1
                
                # Firestore batch limit is 500
                if batch_count >= 500:
                    batch.commit()
                    batch = self.firestore.batch()
                    batch_count = 0
            
            # Commit remaining
            if batch_count > 0:
                batch.commit()
            
            # Delete thread metadata
            self.firestore.collection('chat_threads').document(thread_id).delete()
            
            logger.info(f"Cleared {deleted_count} messages from thread {thread_id}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to clear thread: {e}")
            raise
    
    async def _update_thread_activity(
        self,
        thread_id: str,
        user_id: str
    ):
        """Update thread last activity timestamp."""
        try:
            thread_ref = self.firestore.collection('chat_threads').document(thread_id)
            thread_doc = thread_ref.get()
            
            if thread_doc.exists:
                # Update existing thread
                thread_ref.update({
                    'last_activity': firestore.SERVER_TIMESTAMP,
                    'updated_at': datetime.utcnow().isoformat()
                })
            else:
                # Create new thread metadata
                thread_ref.set({
                    'user_id': user_id,
                    'thread_id': thread_id,
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'last_activity': firestore.SERVER_TIMESTAMP,
                    'message_count': 0
                })
                
        except Exception as e:
            logger.error(f"Failed to update thread activity: {e}")
    
    async def set_active_thread(
        self,
        user_id: str,
        thread_id: str
    ):
        """
        Set the user's active thread.
        This is used to track where monitoring updates should be sent.
        
        Args:
            user_id: User ID
            thread_id: Thread ID to set as active
        """
        try:
            user_profile_ref = self.firestore.collection('user_profiles').document(user_id)
            user_profile_ref.set({
                'active_thread_id': thread_id,
                'updated_at': firestore.SERVER_TIMESTAMP
            }, merge=True)
            
            logger.debug(f"Set active thread for user {user_id} to {thread_id}")
            
        except Exception as e:
            logger.error(f"Failed to set active thread: {e}")
    
    async def get_active_thread(
        self,
        user_id: str
    ) -> Optional[str]:
        """
        Get the user's currently active thread ID.
        
        Args:
            user_id: User ID
            
        Returns:
            Active thread ID if set, None otherwise
        """
        try:
            user_profile_ref = self.firestore.collection('user_profiles').document(user_id)
            user_profile = user_profile_ref.get()
            
            if user_profile.exists:
                data = user_profile.to_dict()
                return data.get('active_thread_id')
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get active thread: {e}")
            return None
