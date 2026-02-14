"""
Monitoring configuration tools.

These tools create and manage monitoring job configurations.
The create_monitoring_config tool triggers HITL approval and then creates
the actual monitoring job via CronService.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from langchain.tools import tool

logger = logging.getLogger(__name__)

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
    logger.info(f"[MONITORING_TOOLS] Services configured - user_id: {user_id}, cron_service: {cron_service is not None}, firestore: {firestore_client is not None}")


@tool
async def create_monitoring_config(
    competitor: str,
    aspects: List[str],
    frequency_hours: float = 6,
    notification_preference: str = "significant_only",
) -> dict:
    """
    Create a monitoring configuration for continuous, automated competitor tracking.

    USE THIS TOOL when the user:
    - Wants to "monitor", "track", or "watch" a competitor continuously
    - Asks for scheduled/recurring updates ("daily", "weekly", "every 6 hours")
    - Says: "set up monitoring", "alert me", "notify me", "keep an eye on"
    - After research, if user wants to stay updated on competitor changes
    
    DO NOT USE this tool for:
    - One-time research (use search_competitor or search_competitor_news instead)
    - Checking current status (use search tools first)
    
    IMPORTANT: This tool triggers a human-in-the-loop approval flow.
    After you call this tool, explain to the user that their approval is required.
    When they APPROVE, you'll receive the tool result with job_id - then confirm it's ACTIVE.

    Args:
        competitor: Name of the competitor to monitor (e.g. "Nike", "Spotify", "Amazon").
        aspects: List of aspects to track continuously.
                 Choose from: ["products", "pricing", "news", "social"]
                 Example: ["news", "products"] to track launches and announcements
                 
        frequency_hours: How often to check, in hours (default: 6).
                 Common values:
                 - 1.0 = hourly (fast-moving, ~$3.60/month)
                 - 6.0 = every 6 hours (standard, ~$0.60/month)
                 - 24.0 = daily (general awareness, ~$0.15/month)
                 
        notification_preference: When to send notifications.
                 - "significant_only" (RECOMMENDED): Only for important changes
                 - "always": Every check result (high volume)
                 - "never": Store silently, no notifications
    
    Returns:
        dict with:
        - config_id: Unique configuration identifier
        - job_id: Monitoring job ID (after approval)
        - frequency_label: Human-readable frequency
        - estimated_monthly_cost: Cost estimate
        - status: "active" after approval
        
    Example:
        User: "Monitor Nike daily"
        → create_monitoring_config(
            competitor="Nike",
            aspects=["news", "products"],
            frequency_hours=24.0,
            notification_preference="significant_only"
        )
        Then say: "I've prepared a monitoring configuration. Please review and approve."
        After approval confirmation: "✅ Monitoring activated! Job ID: [job_id]"
    """
    logger.info(f"[HITL_TOOL] 🔧 create_monitoring_config CALLED")
    logger.info(f"[HITL_TOOL] Parameters - competitor: {competitor}, aspects: {aspects}")
    logger.info(f"[HITL_TOOL] frequency_hours: {frequency_hours}, notification: {notification_preference}")
    logger.info(f"[HITL_TOOL] ⚠️ This tool should trigger HITL approval flow")
    
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
    logger.info(f"[HITL_TOOL] Generated config_id: {config_id}")
    
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
        logger.info(f"[HITL_TOOL] Saving config to Firestore: {config_id}")
        _firestore_client.collection('monitoring_configs').document(config_id).set(config_data)
        logger.info(f"[HITL_TOOL] ✅ Config saved to Firestore")
    else:
        logger.warning(f"[HITL_TOOL] ⚠️ No Firestore client, skipping config save")
    
    # Create the actual monitoring job via CronService
    job_id = None
    if _cron_service:
        logger.info(f"[HITL_TOOL] Creating monitoring job via CronService...")
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
            logger.info(f"[HITL_TOOL] ✅ Monitoring job created: {job_id}")
        except Exception as e:
            config_data["job_status"] = f"error: {str(e)}"
            logger.error(f"[HITL_TOOL] ❌ Failed to create monitoring job: {e}", exc_info=True)
            # Still return config even if job creation fails
    else:
        logger.warning(f"[HITL_TOOL] ⚠️ No CronService, skipping job creation")
    
    logger.info(f"[HITL_TOOL] 🎯 Returning config data: {config_id}")
    return config_data
