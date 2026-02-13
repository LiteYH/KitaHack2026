"""
Cron Jobs Management API Router.

Provides endpoints for managing scheduled monitoring jobs:
- List all jobs for current user
- Pause/resume jobs
- Delete jobs
- Get job execution results
"""
import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.firebase import get_db
from app.core.auth import get_current_user_id
from app.services.cron_service import CronService
from app.services.monitoring_service import monitoring_service
from app.services.notification_service import notification_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crons", tags=["crons"])


def get_cron_service() -> CronService:
    """Get the CronService singleton initialized in main.py"""
    # Import here to avoid circular dependency
    from main import cron_service_instance
    
    if cron_service_instance is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CronService is not initialized. Please check server startup logs.",
        )
    return cron_service_instance


# ── Response Models ──────────────────────────────────────────────────

class CronJobResponse(BaseModel):
    """Cron job details"""
    id: str
    job_id: str
    competitor: str
    aspects: List[str]
    frequency_hours: float
    notification_preference: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    next_run: Optional[datetime] = None
    last_execution: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None


class MonitoringResultResponse(BaseModel):
    """Monitoring execution result"""
    id: str
    config_id: str
    competitor: str
    aspects: List[str]
    execution_time: datetime
    is_significant: bool
    significance_score: int
    summary: str
    notification_sent: bool


class StatusResponse(BaseModel):
    """Simple status response"""
    status: str
    job_id: str
    message: Optional[str] = None


class BulkDeleteRequest(BaseModel):
    """Bulk delete request"""
    job_ids: List[str] = Field(..., min_length=1, description="Job IDs to delete")


class BulkDeleteResponse(BaseModel):
    """Bulk delete response"""
    status: str
    deleted: int
    requested: int
    errors: List[str] = []


class CronJobUpdateRequest(BaseModel):
    """Cron job update request"""
    frequency_hours: Optional[float] = Field(default=None, ge=0)
    aspects: Optional[List[str]] = None
    notification_preference: Optional[str] = None


# ── Endpoints ────────────────────────────────────────────────────────

@router.get("/", response_model=List[CronJobResponse])
async def list_cron_jobs(
    user_id: str = Depends(get_current_user_id),
    cron_service: CronService = Depends(get_cron_service)
):
    """
    List all cron jobs for the current user.
    
    Returns active and paused jobs with their execution status.
    """
    try:
        jobs = await cron_service.list_jobs(user_id)
        return jobs
    except Exception as e:
        logger.error(f"Failed to list jobs for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")


@router.post("/{job_id}/pause", response_model=StatusResponse)
async def pause_job(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
    cron_service: CronService = Depends(get_cron_service)
):
    """
    Pause a scheduled monitoring job.
    
    The job will stop executing until resumed.
    """
    try:
        # TODO: Verify user owns this job before pausing
        result = await cron_service.pause_job(job_id)
        return StatusResponse(
            status=result['status'],
            job_id=result['job_id'],
            message="Job paused successfully"
        )
    except Exception as e:
        logger.error(f"Failed to pause job {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to pause job: {str(e)}")


@router.post("/{job_id}/resume", response_model=StatusResponse)
async def resume_job(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
    cron_service: CronService = Depends(get_cron_service)
):
    """
    Resume a paused monitoring job.
    
    The job will start executing again on its schedule.
    """
    try:
        # TODO: Verify user owns this job before resuming
        result = await cron_service.resume_job(job_id)
        return StatusResponse(
            status=result['status'],
            job_id=result['job_id'],
            message="Job resumed successfully"
        )
    except Exception as e:
        logger.error(f"Failed to resume job {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to resume job: {str(e)}")


@router.delete("/{job_id}", response_model=StatusResponse)
async def delete_job(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
    cron_service: CronService = Depends(get_cron_service)
):
    """
    Delete a monitoring job permanently.
    
    This action cannot be undone. The job will stop executing
    and will be removed from the system.
    """
    try:
        # TODO: Verify user owns this job before deleting
        result = await cron_service.delete_job(job_id)
        return StatusResponse(
            status=result['status'],
            job_id=result['job_id'],
            message="Job deleted successfully"
        )
    except Exception as e:
        logger.error(f"Failed to delete job {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete job: {str(e)}")


@router.post("/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_jobs(
    request: BulkDeleteRequest,
    user_id: str = Depends(get_current_user_id),
    cron_service: CronService = Depends(get_cron_service)
):
    """
    Delete multiple monitoring jobs.
    """
    try:
        result = await cron_service.delete_jobs(request.job_ids)
        return BulkDeleteResponse(**result)
    except Exception as e:
        logger.error(f"Failed to bulk delete jobs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to bulk delete jobs: {str(e)}")


@router.put("/{job_id}", response_model=StatusResponse)
async def update_job(
    job_id: str,
    request: CronJobUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    cron_service: CronService = Depends(get_cron_service)
):
    """
    Update a monitoring job's schedule and configuration.
    """
    try:
        result = await cron_service.update_job(job_id, request.model_dump(exclude_none=True))
        return StatusResponse(
            status=result['status'],
            job_id=result['job_id'],
            message="Job updated successfully"
        )
    except Exception as e:
        logger.error(f"Failed to update job {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update job: {str(e)}")


@router.get("/{config_id}/results", response_model=List[MonitoringResultResponse])
async def get_job_results(
    config_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    cron_service: CronService = Depends(get_cron_service)
):
    """
    Get recent execution results for a monitoring job.
    
    Args:
        config_id: Monitoring configuration ID
        limit: Maximum number of results to return (1-100)
    
    Returns:
        List of monitoring results, sorted by most recent first
    """
    try:
        # TODO: Verify user owns this config before returning results
        results = await cron_service.get_job_results(config_id, limit)
        return results
    except Exception as e:
        logger.error(f"Failed to get results for config {config_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get job results: {str(e)}")


@router.get("/stats/summary")
async def get_cron_stats(
    user_id: str = Depends(get_current_user_id),
    cron_service: CronService = Depends(get_cron_service)
):
    """
    Get summary statistics for user's monitoring jobs.
    
    Returns counts of active, paused, and failed jobs.
    """
    try:
        jobs = await cron_service.list_jobs(user_id)
        
        stats = {
            'total': len(jobs),
            'active': sum(1 for j in jobs if j.get('status') == 'running'),
            'paused': sum(1 for j in jobs if j.get('status') == 'paused'),
            'failed': sum(1 for j in jobs if j.get('status') == 'failed'),
            'with_errors': sum(1 for j in jobs if j.get('error_count', 0) > 0)
        }
        
        return stats
    except Exception as e:
        logger.error(f"Failed to get stats for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")
