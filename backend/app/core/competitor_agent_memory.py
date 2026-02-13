"""
Hybrid Memory Manager for Competitor Monitoring Agent.

Combines LangGraph's InMemorySaver (thread-level checkpoints)
with Firestore (cross-thread persistent memory).

Uses the 'competitor_agent_memory' collection for storing agent context.
Thread-level conversation memory is stored in-memory.
"""

import os
from typing import Any, Dict, Optional

from google.cloud.firestore import Client as FirestoreClient
from langgraph.checkpoint.memory import InMemorySaver


class HybridMemoryManager:
    """
    Manages thread-level checkpoints (InMemorySaver) and
    cross-thread persistent memory (Firestore).
    
    Thread memory (InMemorySaver):
    - Persists conversation state per thread_id in memory
    - Enables multi-turn conversations with context
    - Note: Memory is cleared on server restart
    
    Long-term memory (Firestore):
    - competitor_agent_memory: Agent context and user preferences
    - monitoring_jobs: Active monitoring configurations
    - monitoring_logs: Historical monitoring results
    - chat_threads: Conversation metadata
    """

    def __init__(self, firestore_client: Optional[FirestoreClient] = None, db_path: str = "./data/checkpoints.db"):
        # Use InMemorySaver for thread-level memory
        # This stores conversation state and allows resuming conversations
        # Note: Memory is in-memory only and cleared on restart
        self.checkpointer = InMemorySaver()
        self.firestore = firestore_client

    # ── Cross-thread memory (Firestore) ──────────────────────────────

    def save_user_memory(self, user_id: str, data: Dict[str, Any]) -> None:
        """
        Save / merge cross-thread memory for a user.
        
        Stores in 'competitor_agent_memory' collection.
        """
        if not self.firestore:
            return
        self.firestore.collection("competitor_agent_memory").document(user_id).set(
            data, merge=True
        )

    def get_user_memory(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve a user's cross-thread memory.
        
        Reads from 'competitor_agent_memory' collection.
        """
        if not self.firestore:
            return {}
        doc = self.firestore.collection("competitor_agent_memory").document(user_id).get()
        return doc.to_dict() if doc.exists else {}

    # ── Monitoring configs (Firestore) ───────────────────────────────

    def save_monitoring_config(
        self, config_id: str, config_data: Dict[str, Any]
    ) -> None:
        """
        Persist a monitoring configuration.
        
        Stores in 'monitoring_jobs' collection.
        """
        if not self.firestore:
            return
        self.firestore.collection("monitoring_jobs").document(config_id).set(
            config_data, merge=True
        )

    def get_monitoring_configs(self, user_id: str):
        """
        Get all monitoring configs for a user.
        
        Reads from 'monitoring_jobs' collection.
        """
        if not self.firestore:
            return []
        docs = (
            self.firestore.collection("monitoring_jobs")
            .where("userId", "==", user_id)
            .stream()
        )
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]

    # ── Monitoring logs (Firestore) ──────────────────────────────────

    def save_monitoring_log(
        self, log_id: str, log_data: Dict[str, Any]
    ) -> None:
        """
        Save a monitoring result/log.
        
        Stores in 'monitoring_logs' collection.
        """
        if not self.firestore:
            return
        self.firestore.collection("monitoring_logs").document(log_id).set(
            log_data, merge=True
        )

    def get_monitoring_logs(self, user_id: str, limit: int = 50):
        """
        Get recent monitoring logs for a user.
        
        Reads from 'monitoring_logs' collection.
        """
        if not self.firestore:
            return []
        docs = (
            self.firestore.collection("monitoring_logs")
            .where("userId", "==", user_id)
            .order_by("timestamp", direction="DESCENDING")
            .limit(limit)
            .stream()
        )
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]

    # ── Chat thread backup (Firestore) ───────────────────────────────

    def save_thread_metadata(
        self, thread_id: str, data: Dict[str, Any]
    ) -> None:
        """Backup thread metadata to Firestore for persistence."""
        if not self.firestore:
            return
        self.firestore.collection("chat_threads").document(thread_id).set(
            data, merge=True
        )

    def get_thread_metadata(self, thread_id: str) -> Dict[str, Any]:
        """Retrieve thread metadata."""
        if not self.firestore:
            return {}
        doc = self.firestore.collection("chat_threads").document(thread_id).get()
        return doc.to_dict() if doc.exists else {}
