"""
Cron Service for managing scheduled monitoring jobs using APScheduler.
Syncs with Firestore for persistence and handles job lifecycle.
"""
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.triggers.interval import IntervalTrigger
from google.cloud import firestore

logger = logging.getLogger(__name__)


class CronService:
    """
    Manages scheduled monitoring jobs using APScheduler.
    Syncs with Firestore for persistence.
    """
    
    def __init__(self, firestore_client: firestore.Client, monitoring_service=None, notification_service=None):
        """
        Initialize CronService with Firestore and optionally monitoring/notification services.
        
        Args:
            firestore_client: Firestore client
            monitoring_service: MonitoringService instance (can be set later)
            notification_service: NotificationService instance (can be set later)
        """
        self.firestore = firestore_client
        self.monitoring_service = monitoring_service
        self.notification_service = notification_service
        
        # Configure APScheduler with in-memory jobstore
        # Note: Jobs will not persist across server restarts
        # For production, consider using a Redis jobstore or refactoring to use standalone task functions
        jobstores = {
            'default': MemoryJobStore()
        }
        
        self.scheduler = AsyncIOScheduler(jobstores=jobstores)
        self._scheduler_started = False
        logger.info("APScheduler initialized (not started yet)")
    
    async def start(self):
        """Start the scheduler. Must be called in an async context with a running event loop."""
        if not self._scheduler_started:
            self.scheduler.start()
            self._scheduler_started = True
            logger.info("APScheduler started successfully with in-memory job store")
    
    def set_monitoring_service(self, monitoring_service):
        """Set the monitoring service (used to break circular dependencies)"""
        self.monitoring_service = monitoring_service
    
    def set_notification_service(self, notification_service):
        """Set the notification service (used to break circular dependencies)"""
        self.notification_service = notification_service
    
    async def create_monitoring_job(
        self,
        config_id: str,
        competitor: str,
        aspects: List[str],
        frequency_hours: float,
        user_id: str,
        notification_preference: str = "significant"
    ) -> str:
        """
        Create and schedule a monitoring job.
        
        Args:
            config_id: Monitoring configuration ID
            competitor: Competitor name to monitor
            aspects: List of aspects to monitor (products, pricing, social, news)
            frequency_hours: How often to run (in hours)
            user_id: User ID who created the job
            notification_preference: When to send notifications (always/significant/never)
            
        Returns:
            job_id: Generated job ID
        """
        # Generate unique job ID
        job_id = f"monitor_{uuid.uuid4().hex[:8]}"
        
        # Calculate next run time (10 seconds from now for first run)
        next_run = datetime.utcnow() + timedelta(seconds=10)
        
        try:
            min_seconds = 60
            interval_seconds = max(min_seconds, int(frequency_hours * 3600))

            # Add job to APScheduler
            self.scheduler.add_job(
                func=self._execute_monitoring_task,
                trigger=IntervalTrigger(seconds=interval_seconds),
                id=job_id,
                args=[config_id, competitor, aspects, user_id, notification_preference],
                replace_existing=True,
                next_run_time=next_run
            )
            
            logger.info(f"Created APScheduler job: {job_id} for {competitor}")
            
            # Save job metadata to Firestore
            self.firestore.collection('cron_jobs').document(job_id).set({
                'config_id': config_id,
                'apscheduler_id': job_id,
                'status': 'running',
                'created_at': firestore.SERVER_TIMESTAMP,
                'next_run': next_run,
                'error_count': 0,
                'last_execution': None,
                'last_error': None
            })
            
            # Update monitoring config with job ID
            self.firestore.collection('monitoring_configs').document(config_id).update({
                'apscheduler_job_id': job_id,
                'status': 'active',
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            logger.info(f"Cron job {job_id} created successfully")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to create monitoring job: {e}")
            raise
    
    async def _execute_monitoring_task(
        self,
        config_id: str,
        competitor: str,
        aspects: List[str],
        user_id: str,
        notification_preference: str
    ):
        """
        Execute monitoring task (called by APScheduler).
        This runs the competitor monitoring agent and saves results.
        
        Args:
            config_id: Configuration ID
            competitor: Competitor to monitor
            aspects: Aspects to monitor
            user_id: User ID
            notification_preference: Notification preference
        """
        result_id = uuid.uuid4().hex
        execution_time = datetime.utcnow()
        
        try:
            logger.info(f"Executing monitoring task for {competitor} (config: {config_id})")
            
            if not self.monitoring_service:
                raise RuntimeError("MonitoringService not initialized")
            
            # Execute monitoring using the monitoring service
            results = await self.monitoring_service.execute_monitoring(
                competitor=competitor,
                aspects=aspects,
                user_id=user_id
            )
            
            # Save results to Firestore
            self.firestore.collection('monitoring_results').document(result_id).set({
                'config_id': config_id,
                'competitor': competitor,
                'aspects': aspects,
                'execution_time': firestore.SERVER_TIMESTAMP,
                'findings': results.get('findings', {}),
                'is_significant': results.get('is_significant', False),
                'significance_score': results.get('significance_score', 0),
                'summary': results.get('summary', ''),
                'notification_sent': False,
                'user_id': user_id
            })
            
            logger.info(f"Monitoring results saved: {result_id}")
            
            # Save as chat message for proactive notification
            await self._save_monitoring_as_chat_message(
                user_id=user_id,
                competitor=competitor,
                aspects=aspects,
                results=results,
                result_id=result_id,
                execution_time=execution_time
            )
            
            # Send notification if needed
            should_notify = (
                (notification_preference == "always") or
                (notification_preference == "significant" and results.get('is_significant', False))
            )
            
            if should_notify:
                try:
                    if not self.notification_service:
                        logger.warning("NotificationService not initialized, skipping notification")
                    else:
                        await self.notification_service.send_monitoring_notification(
                            user_id=user_id,
                            competitor=competitor,
                            findings=results.get('findings', {}),
                            summary=results.get('summary', ''),
                            significance_score=results.get('significance_score', 0),
                            reasons=results.get('reasons', [])
                        )
                    
                        # Update notification status
                        self.firestore.collection('monitoring_results').document(result_id).update({
                            'notification_sent': True
                        })
                        
                        logger.info(f"Notification sent for {result_id}")
                except Exception as notif_error:
                    logger.error(f"Failed to send notification: {notif_error}")
            
            # Reset error count on successful execution
            job = self.scheduler.get_job(self._get_job_id_from_config(config_id))
            if job:
                self.firestore.collection('cron_jobs').document(job.id).update({
                    'error_count': 0,
                    'last_execution': firestore.SERVER_TIMESTAMP,
                    'last_error': None
                })
            
            logger.info(f"Monitoring task completed successfully for {competitor}")
            
        except Exception as e:
            logger.error(f"Monitoring task failed for {competitor}: {e}", exc_info=True)
            
            # Increment error count
            try:
                job_doc = self.firestore.collection('cron_jobs').where(
                    'config_id', '==', config_id
                ).limit(1).get()
                
                if job_doc:
                    job_data = job_doc[0].to_dict()
                    error_count = job_data.get('error_count', 0) + 1
                    job_id = job_doc[0].id
                    
                    self.firestore.collection('cron_jobs').document(job_id).update({
                        'error_count': error_count,
                        'last_error': str(e),
                        'last_execution': firestore.SERVER_TIMESTAMP,
                        'status': 'failed' if error_count >= 3 else 'running'
                    })
                    
                    # Pause job if too many errors
                    if error_count >= 3:
                        logger.warning(f"Job {job_id} paused due to repeated failures")
                        self.scheduler.pause_job(job_id)
            except Exception as update_error:
                logger.error(f"Failed to update error count: {update_error}")
    
    def _get_job_id_from_config(self, config_id: str) -> Optional[str]:
        """Helper to get job ID from config ID"""
        # This would need to query Firestore, but for now we can use the scheduler
        for job in self.scheduler.get_jobs():
            if job.args and job.args[0] == config_id:
                return job.id
        return None
    
    async def _save_monitoring_as_chat_message(
        self,
        user_id: str,
        competitor: str,
        aspects: List[str],
        results: Dict[str, Any],
        result_id: str,
        execution_time: datetime
    ):
        """
        Save monitoring results as a chat message for proactive notification.
        
        Args:
            user_id: User ID
            competitor: Competitor name
            aspects: Monitored aspects
            results: Monitoring results
            result_id: Result document ID
            execution_time: When the monitoring was executed
        """
        try:
            # Format the message content
            significance = "🔴 Significant" if results.get('is_significant') else "🟢 Normal"
            score = results.get('significance_score', 0)
            summary = results.get('summary', 'No summary available')
            
            # Build detailed findings
            findings_text = ""
            if 'findings' in results:
                findings = results['findings']
                if isinstance(findings, dict):
                    for aspect, data in findings.items():
                        if isinstance(data, dict):
                            findings_text += f"\n**{aspect.capitalize()}:**\n"
                            if 'summary' in data:
                                findings_text += f"{data['summary']}\n"
                            elif 'articles' in data and data['articles']:
                                for article in data['articles'][:3]:  # Top 3 articles
                                    if isinstance(article, dict):
                                        title = article.get('title', 'No title')
                                        findings_text += f"  • {title}\n"
            
            message_content = f"""**🔍 Competitor Monitoring Update**

**Competitor:** {competitor}
**Aspects Monitored:** {', '.join(aspects)}
**Status:** {significance} (Score: {score}/100)
**Time:** {execution_time.strftime('%Y-%m-%d %H:%M UTC')}

**Summary:**
{summary}
{findings_text}

_Result ID: {result_id}_
"""
            
            # Save to a chat messages collection
            message_id = uuid.uuid4().hex
            self.firestore.collection('chat_messages').document(message_id).set({
                'user_id': user_id,
                'message': message_content,
                'type': 'monitoring_update',
                'sender': 'system',
                'timestamp': firestore.SERVER_TIMESTAMP,
                'metadata': {
                    'competitor': competitor,
                    'aspects': aspects,
                    'is_significant': results.get('is_significant', False),
                    'significance_score': score,
                    'result_id': result_id,
                    'config_id': results.get('config_id', '')
                }
            })
            
            logger.info(f"Saved monitoring result as chat message: {message_id} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to save monitoring as chat message: {e}", exc_info=True)
    
    async def pause_job(self, job_id: str) -> Dict[str, str]:
        """
        Pause a monitoring job.
        
        Args:
            job_id: Job ID to pause
            
        Returns:
            Status dict
        """
        try:
            self.scheduler.pause_job(job_id)
            
            self.firestore.collection('cron_jobs').document(job_id).update({
                'status': 'paused',
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            logger.info(f"Job {job_id} paused")
            return {"status": "paused", "job_id": job_id}
            
        except Exception as e:
            logger.error(f"Failed to pause job {job_id}: {e}")
            raise
    
    async def resume_job(self, job_id: str) -> Dict[str, str]:
        """
        Resume a paused job.
        
        Args:
            job_id: Job ID to resume
            
        Returns:
            Status dict
        """
        try:
            self.scheduler.resume_job(job_id)
            
            self.firestore.collection('cron_jobs').document(job_id).update({
                'status': 'running',
                'updated_at': firestore.SERVER_TIMESTAMP,
                'error_count': 0  # Reset error count on resume
            })
            
            logger.info(f"Job {job_id} resumed")
            return {"status": "running", "job_id": job_id}
            
        except Exception as e:
            logger.error(f"Failed to resume job {job_id}: {e}")
            raise
    
    async def delete_job(self, job_id: str) -> Dict[str, str]:
        """
        Delete a monitoring job.
        
        Args:
            job_id: Job ID to delete
            
        Returns:
            Status dict
        """
        try:
            # Remove from APScheduler
            self.scheduler.remove_job(job_id)
            
            # Get config ID before deleting job record
            job_doc = self.firestore.collection('cron_jobs').document(job_id).get()
            
            if job_doc.exists:
                job_data = job_doc.to_dict()
                config_id = job_data.get('config_id')
                
                # Delete job record
                self.firestore.collection('cron_jobs').document(job_id).delete()
                
                # Update monitoring config status
                if config_id:
                    self.firestore.collection('monitoring_configs').document(config_id).update({
                        'status': 'deleted',
                        'updated_at': firestore.SERVER_TIMESTAMP
                    })
            
            logger.info(f"Job {job_id} deleted")
            return {"status": "deleted", "job_id": job_id}
            
        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {e}")
            raise

    async def delete_jobs(self, job_ids: List[str]) -> Dict[str, Any]:
        """
        Delete multiple monitoring jobs.

        Args:
            job_ids: List of job IDs to delete

        Returns:
            Summary of deletions
        """
        deleted = 0
        errors: List[str] = []

        for job_id in job_ids:
            try:
                await self.delete_job(job_id)
                deleted += 1
            except Exception as e:
                errors.append(f"{job_id}: {str(e)}")

        return {
            "status": "completed",
            "deleted": deleted,
            "requested": len(job_ids),
            "errors": errors
        }

    async def update_job(self, job_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a monitoring job's configuration and schedule.

        Supported updates: frequency_hours, aspects, notification_preference.
        """
        try:
            job_doc = self.firestore.collection('cron_jobs').document(job_id).get()
            if not job_doc.exists:
                raise ValueError(f"Job {job_id} not found")

            job_data = job_doc.to_dict()
            config_id = job_data.get('config_id')
            if not config_id:
                raise ValueError(f"Job {job_id} missing config_id")

            config_updates: Dict[str, Any] = {
                'updated_at': firestore.SERVER_TIMESTAMP
            }

            if 'frequency_hours' in updates and updates['frequency_hours'] is not None:
                frequency_hours = float(updates['frequency_hours'])
                min_hours = 1 / 60
                if frequency_hours < min_hours:
                    frequency_hours = min_hours

                interval_seconds = max(60, int(frequency_hours * 3600))
                self.scheduler.reschedule_job(
                    job_id,
                    trigger=IntervalTrigger(seconds=interval_seconds)
                )

                config_updates['frequency_hours'] = frequency_hours
                if frequency_hours < 1:
                    config_updates['frequency_label'] = f"Every {round(frequency_hours * 60)} min"
                else:
                    config_updates['frequency_label'] = f"Every {frequency_hours}h"

            if 'aspects' in updates and updates['aspects'] is not None:
                config_updates['aspects'] = updates['aspects']

            if 'notification_preference' in updates and updates['notification_preference'] is not None:
                config_updates['notification_preference'] = updates['notification_preference']

            if config_updates:
                self.firestore.collection('monitoring_configs').document(config_id).update(config_updates)
                self.firestore.collection('cron_jobs').document(job_id).update({
                    'updated_at': firestore.SERVER_TIMESTAMP
                })

            logger.info(f"Job {job_id} updated")
            return {"status": "updated", "job_id": job_id}

        except Exception as e:
            logger.error(f"Failed to update job {job_id}: {e}")
            raise
    
    async def list_jobs(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all jobs for a user.
        
        Args:
            user_id: User ID to filter jobs
            
        Returns:
            List of job details
        """
        try:
            # Get all active monitoring configs for user
            configs = self.firestore.collection('monitoring_configs').where(
                'user_id', '==', user_id
            ).get()
            
            jobs = []
            for config_doc in configs:
                config_data = config_doc.to_dict()
                if config_data.get('status') not in ['active', 'paused']:
                    continue
                job_id = config_data.get('apscheduler_job_id')
                
                if job_id:
                    # Get job status from cron_jobs collection
                    job_doc = self.firestore.collection('cron_jobs').document(job_id).get()
                    
                    if job_doc.exists:
                        job_data = job_doc.to_dict()
                        
                        # Get next run time from scheduler
                        scheduler_job = self.scheduler.get_job(job_id)
                        next_run = scheduler_job.next_run_time if scheduler_job else None
                        
                        jobs.append({
                            'id': config_doc.id,
                            'job_id': job_id,
                            'competitor': config_data.get('competitor'),
                            'aspects': config_data.get('aspects', []),
                            'frequency_hours': config_data.get('frequency_hours'),
                            'notification_preference': config_data.get('notification_preference'),
                            'status': job_data.get('status'),
                            'created_at': config_data.get('created_at'),
                            'next_run': next_run,
                            'last_execution': job_data.get('last_execution'),
                            'error_count': job_data.get('error_count', 0),
                            'last_error': job_data.get('last_error')
                        })
            
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to list jobs for user {user_id}: {e}")
            raise
    
    async def get_job_results(
        self,
        config_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get recent results for a monitoring job.
        
        Args:
            config_id: Configuration ID
            limit: Maximum number of results to return
            
        Returns:
            List of monitoring results
        """
        try:
            results_query = self.firestore.collection('monitoring_results').where(
                'config_id', '==', config_id
            ).order_by('execution_time', direction=firestore.Query.DESCENDING).limit(limit)
            
            results_docs = results_query.get()
            
            results = []
            for doc in results_docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get job results for {config_id}: {e}")
            raise
    
    async def load_jobs_on_startup(self):
        """
        Load active jobs from Firestore on server startup.
        Recreate APScheduler jobs that were running.
        """
        try:
            logger.info("Loading active jobs from Firestore...")
            
            # Get all running jobs (Firestore client is sync, not async)
            jobs = self.firestore.collection('cron_jobs').where(
                'status', '==', 'running'
            ).get()
            
            loaded_count = 0
            for job_doc in jobs:
                job_data = job_doc.to_dict()
                config_id = job_data.get('config_id')
                
                # Get config details
                config = self.firestore.collection('monitoring_configs').document(config_id).get()
                
                if config.exists:
                    config_data = config.to_dict()
                    
                    # Recreate job
                    await self.create_monitoring_job(
                        config_id=config_id,
                        competitor=config_data.get('competitor'),
                        aspects=config_data.get('aspects', []),
                        frequency_hours=config_data.get('frequency_hours'),
                        user_id=config_data.get('user_id'),
                        notification_preference=config_data.get('notification_preference', 'significant')
                    )
                    loaded_count += 1
            
            logger.info(f"Loaded {loaded_count} active jobs on startup")
            
        except Exception as e:
            logger.error(f"Failed to load jobs on startup: {e}")
            # Don't raise - continue app startup even if job loading fails
    
    def shutdown(self):
        """Shutdown the scheduler gracefully"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            self._scheduler_started = False
            logger.info("APScheduler shut down successfully")
