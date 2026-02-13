"""
Monitoring Database Service
Simple helper functions for working with the competitor monitoring database.
"""

import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from google.cloud import firestore


class MonitoringDBService:
    """Service for interacting with monitoring database collections"""
    
    def __init__(self, db: firestore.Client):
        self.db = db
    
    # ==================== COMPETITORS ====================
    
    async def create_competitor(self, user_id: str, name: str, url: str) -> str:
        """Create a new competitor entry"""
        doc_ref = self.db.collection('competitors').add({
            'userId': user_id,
            'name': name,
            'url': url,
            'createdAt': firestore.SERVER_TIMESTAMP
        })
        return doc_ref[1].id
    
    async def get_user_competitors(self, user_id: str) -> List[Dict]:
        """Get all competitors for a user"""
        docs = self.db.collection('competitors')\
            .where('userId', '==', user_id)\
            .stream()
        
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    # ==================== MONITORING JOBS ====================
    
    async def create_monitoring_job(
        self,
        user_id: str,
        competitor: str,
        config: Dict,
        cron_job_id: str
    ) -> str:
        """
        Create a new monitoring job
        
        Config example:
        {
            "aspects": ["products", "news"],
            "frequency_hours": 2,
            "notification": "significant",
            "email": "user@example.com"
        }
        """
        frequency_hours = config.get('frequency_hours', 24)
        
        doc_ref = self.db.collection('monitoring_jobs').add({
            'userId': user_id,
            'competitor': competitor,
            'config': json.dumps(config),  # Store as JSON string
            'status': 'active',
            'cronJobId': cron_job_id,
            'nextRun': datetime.utcnow() + timedelta(hours=frequency_hours),
            'lastRun': None,
            'createdAt': firestore.SERVER_TIMESTAMP
        })
        
        return doc_ref[1].id
    
    async def get_monitoring_job(self, job_id: str) -> Optional[Dict]:
        """Get a monitoring job by ID"""
        doc = self.db.collection('monitoring_jobs').document(job_id).get()
        
        if doc.exists:
            data = doc.to_dict()
            # Parse config JSON
            data['config'] = json.loads(data['config'])
            return {'id': doc.id, **data}
        
        return None
    
    async def get_user_monitoring_jobs(
        self,
        user_id: str,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get all monitoring jobs for a user"""
        query = self.db.collection('monitoring_jobs')\
            .where('userId', '==', user_id)
        
        if status:
            query = query.where('status', '==', status)
        
        docs = query.stream()
        
        result = []
        for doc in docs:
            data = doc.to_dict()
            # Parse config JSON
            data['config'] = json.loads(data['config'])
            result.append({'id': doc.id, **data})
        
        return result
    
    async def update_job_status(self, job_id: str, status: str):
        """Update monitoring job status (active/paused)"""
        self.db.collection('monitoring_jobs').document(job_id).update({
            'status': status
        })
    
    async def update_job_run_time(self, job_id: str, next_run: datetime):
        """Update next run time after execution"""
        self.db.collection('monitoring_jobs').document(job_id).update({
            'lastRun': firestore.SERVER_TIMESTAMP,
            'nextRun': next_run
        })
    
    async def delete_monitoring_job(self, job_id: str):
        """Delete a monitoring job"""
        self.db.collection('monitoring_jobs').document(job_id).delete()
    
    # ==================== MONITORING LOGS ====================
    
    async def create_monitoring_log(
        self,
        user_id: str,
        job_id: str,
        competitor: str,
        findings: Dict,
        notified: bool = False
    ) -> str:
        """
        Create a monitoring log entry
        
        Findings example:
        {
            "products": [...],
            "news": [...],
            "pricing": [...],
            "isSignificant": True,
            "score": 85,
            "reasons": ["New product launch"]
        }
        """
        doc_ref = self.db.collection('monitoring_logs').add({
            'userId': user_id,
            'jobId': job_id,
            'competitor': competitor,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'data': json.dumps(findings),  # Store as JSON string
            'notified': notified
        })
        
        return doc_ref[1].id
    
    async def get_monitoring_logs(
        self,
        user_id: str,
        job_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get monitoring logs for a user"""
        query = self.db.collection('monitoring_logs')\
            .where('userId', '==', user_id)
        
        if job_id:
            query = query.where('jobId', '==', job_id)
        
        query = query.order_by('timestamp', direction=firestore.Query.DESCENDING)\
            .limit(limit)
        
        docs = query.stream()
        
        result = []
        for doc in docs:
            data = doc.to_dict()
            # Parse data JSON
            data['data'] = json.loads(data['data'])
            result.append({'id': doc.id, **data})
        
        return result
    
    async def get_significant_logs(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Dict]:
        """Get only significant monitoring findings"""
        logs = await self.get_monitoring_logs(user_id, limit=100)
        
        # Filter for significant findings
        significant = [
            log for log in logs
            if log['data'].get('isSignificant', False)
        ]
        
        return significant[:limit]
    
    # ==================== AGENT MEMORY ====================
    
    async def get_agent_memory(self, user_id: str) -> Optional[Dict]:
        """Get agent memory for a user"""
        doc = self.db.collection('agent_memory').document(user_id).get()
        
        if doc.exists:
            data = doc.to_dict()
            # Parse memory JSON
            memory_str = data.get('memory', '{}')
            try:
                data['memory'] = json.loads(memory_str)
            except json.JSONDecodeError:
                # If it's markdown or plain text, keep as string
                pass
            
            return data
        
        return None
    
    async def update_agent_memory(self, user_id: str, memory: Dict):
        """
        Update agent memory for a user
        
        Memory example:
        {
            "prefs": {"freq": 6, "notif": "significant"},
            "active": ["Nike", "Adidas"],
            "recent": ["Nike price drop", "Discussed launches"],
            "stats": {"jobs": 5, "findings": 127}
        }
        """
        self.db.collection('agent_memory').document(user_id).set({
            'memory': json.dumps(memory, indent=2),
            'updatedAt': firestore.SERVER_TIMESTAMP
        }, merge=True)
    
    async def append_to_memory_recent(self, user_id: str, topic: str):
        """Append a topic to recent conversation context"""
        current_memory = await self.get_agent_memory(user_id)
        
        if not current_memory:
            memory = {
                "prefs": {},
                "active": [],
                "recent": [topic],
                "stats": {}
            }
        else:
            memory = current_memory.get('memory', {})
            if isinstance(memory, str):
                memory = json.loads(memory)
            
            if 'recent' not in memory:
                memory['recent'] = []
            
            memory['recent'].insert(0, topic)
            memory['recent'] = memory['recent'][:10]  # Keep last 10
        
        await self.update_agent_memory(user_id, memory)
    
    # ==================== HELPER FUNCTIONS ====================
    
    async def get_dashboard_stats(self, user_id: str) -> Dict:
        """Get dashboard statistics for a user"""
        
        # Count active jobs
        active_jobs = await self.get_user_monitoring_jobs(user_id, status='active')
        
        # Count competitors
        competitors = await self.get_user_competitors(user_id)
        
        # Count total logs
        logs = await self.get_monitoring_logs(user_id, limit=1000)
        
        # Count significant findings
        significant = [log for log in logs if log['data'].get('isSignificant')]
        
        return {
            'activeJobs': len(active_jobs),
            'totalCompetitors': len(competitors),
            'totalFindings': len(logs),
            'significantFindings': len(significant),
            'competitors': [job['competitor'] for job in active_jobs]
        }
