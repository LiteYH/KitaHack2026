"""
Monitoring configuration tools.

These tools create and manage monitoring job configurations.
The create_monitoring_config tool triggers HITL approval and then creates
the actual monitoring job via CronService.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from langchain.tools import tool

# Module-level variables to store service instances
_cron_service = None
_firestore_client = None
_user_id = None


def set_monitoring_services(cron_service, firestore_client, user_id: Optional[str] = None):
    """
    Set the monitoring services for the tools.
    Call this before creating the agent.
    """
    global _cron_service, _firestore_client, _user_id
    _cron_service = cron_service
    _firestore_client = firestore_client
    _user_id = user_id


@tool
async def create_monitoring_config(
    competitor: str,
    aspects: List[str],
    frequency_hours: float = 6,
    notification_preference: str = "significant_only",
) -> dict:
    """
    Create a monitoring configuration for continuous competitor tracking.

    This will set up a scheduled job to automatically monitor the specified
    competitor at the given frequency. This triggers a human-in-the-loop 
    approval flow before the job is created.

    After approval, the monitoring job will be created and activated automatically.

    Args:
        competitor: Name of the competitor to monitor.
        aspects: List of aspects to track.
                 Choose from: ["products", "pricing", "news", "social"]
        frequency_hours: How often to check, in hours (default: 6).
                 Supports sub-hour values (e.g., 0.0167 = 1 minute)
        notification_preference: When to send notifications.
                                  Options: "always", "significant_only", "never"
    
    Returns:
        dict: Configuration details and job creation status
    """
    frequency_labels = {
        1: "Every hour",
        2: "Every 2 hours",
        6: "Every 6 hours",
        12: "Twice daily",
        24: "Daily",
    }

    min_hours = 1 / 60
    if frequency_hours < min_hours:
        frequency_hours = min_hours

    cost_per_run = 0.05  # estimated
    runs_per_month = (24 / frequency_hours) * 30
    monthly_cost = cost_per_run * runs_per_month

    # Generate config ID
    config_id = f"config_{uuid.uuid4().hex[:12]}"
    
    # Create configuration document in Firestore
    config_data = {
        "config_id": config_id,
        "competitor": competitor,
        "aspects": aspects,
        "frequency_hours": frequency_hours,
        "frequency_label": frequency_labels.get(
            frequency_hours,
            f"Every {round(frequency_hours * 60)} min"
            if frequency_hours < 1
            else f"Every {frequency_hours}h"
        ),
        "notification_preference": notification_preference,
        "estimated_monthly_cost": f"${monthly_cost:.2f}/month",
        "estimated_runs_per_month": int(runs_per_month),
        "status": "active",  # After HITL approval
        "user_id": _user_id or "default_user",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    
    # Save config to Firestore
    if _firestore_client:
        _firestore_client.collection('monitoring_configs').document(config_id).set(config_data)
    
    # Create the actual monitoring job via CronService
    job_id = None
    if _cron_service:
        try:
            job_id = await _cron_service.create_monitoring_job(
                config_id=config_id,
                competitor=competitor,
                aspects=aspects,
                frequency_hours=frequency_hours,
                user_id=_user_id or "default_user",
                notification_preference=notification_preference
            )
            config_data["job_id"] = job_id
            config_data["job_status"] = "created"
        except Exception as e:
            config_data["job_status"] = f"error: {str(e)}"
            # Still return config even if job creation fails
    
    return config_data
