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
from langgraph.errors import GraphInterrupt
from langgraph.types import interrupt as lg_interrupt

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
    
    IMPORTANT: This tool handles HITL approval internally via LangGraph interrupt().
    The graph pauses for user approval BEFORE this tool returns any result.
    When this tool returns (status: 'active', job_id present), approval has ALREADY been
    granted and the job is LIVE. Generate a confirmation message immediately — do NOT
    ask the user to approve again.

    Args:
        competitor: Name of the competitor to monitor (e.g. "Nike", "Spotify", "Amazon").
        aspects: List of aspects to track continuously.
                 Choose from: ["products", "pricing", "news", "social"]
                 Example: ["news", "products"] to track launches and announcements
                 
        frequency_hours: How often to check, in hours (default: 6).
                 Common values:
                 - 1.0 = hourly (fast-moving)
                 - 6.0 = every 6 hours (standard)
                 - 24.0 = daily (general awareness)
                 
        notification_preference: When to send notifications.
                 - "significant_only" (RECOMMENDED): Only for important changes
                 - "always": Every check result (high volume)
                 - "never": Store silently, no notifications
    
    Returns:
        dict with:
        - config_id: Unique configuration identifier
        - job_id: Monitoring job ID (after approval)
        - frequency_label: Human-readable frequency
        - status: "active" after approval
        
    Example:
        User: "Monitor Nike daily"
        → create_monitoring_config(
            competitor="Nike",
            aspects=["news", "products"],
            frequency_hours=24.0,
            notification_preference="significant_only"
        )
        When the tool returns → immediately say: "✅ Monitoring activated! Nike is now being
        tracked daily for news and products. Job ID: [job_id]"
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

    # Generate config ID
    config_id = f"config_{uuid.uuid4().hex[:12]}"
    logger.info(f"[HITL_TOOL] Generated config_id: {config_id}")
    
    # Build config data (not saved yet — awaiting HITL approval)
    frequency_label = frequency_labels.get(
        frequency_hours,
        f"Every {round(frequency_hours * 60)} min" if frequency_hours < 1 else f"Every {frequency_hours}h"
    )
    config_data = {
        "config_id": config_id,
        "competitor": competitor,
        "aspects": aspects,
        "frequency_hours": frequency_hours,
        "frequency_label": frequency_label,
        "notification_preference": notification_preference,
        "status": "active",
        "user_id": _user_id or "default_user",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    # ── Human-in-the-Loop approval (per LangGraph interrupt() pattern) ──────
    # interrupt() pauses execution here and returns the resume value.
    # On the first call it raises GraphInterrupt (graph pauses).
    # On the resume call (after user approves) it returns the decision.
    proposal = {
        "action_requests": [{
            "name": "create_monitoring_config",
            "action": "create_monitoring_config",
            "arguments": {
                "competitor": competitor,
                "aspects": aspects,
                "frequency_hours": frequency_hours,
                "frequency_label": frequency_label,
                "notification_preference": notification_preference,
                "config_id": config_id,
            },
            "args": config_data.copy(),
            "description": (
                f"Set up {frequency_label.lower()} monitoring for **{competitor}** "
                f"tracking: {', '.join(aspects)}. "
                f"Notifications: {notification_preference}."
            ),
        }],
        "review_configs": [{
            "action_name": "create_monitoring_config",
            "allowed_decisions": ["approve", "edit", "reject"],
        }],
    }
    logger.info(f"[HITL_TOOL] ⏳ Waiting for HITL approval (create_monitoring_config)...")
    decision_value = lg_interrupt(proposal)
    logger.info(f"[HITL_TOOL] ✅ HITL resumed with: {decision_value}")

    # Parse decision from resume payload
    decisions_list = decision_value.get("decisions", []) if isinstance(decision_value, dict) else []
    primary = decisions_list[0] if decisions_list else {"type": "approve"}
    decision_type = primary.get("type", "approve")

    if decision_type == "reject":
        rejection_reason = primary.get("feedback") or primary.get("reason") or ""
        logger.info(f"[HITL_TOOL] ❌ create_monitoring_config rejected by user. Reason: {rejection_reason}")
        rejection_message = f"Monitoring setup for {competitor} was rejected."
        if rejection_reason:
            rejection_message += f" User's reason: {rejection_reason}"
        return {
            "status": "rejected",
            "message": rejection_message,
            "rejection_reason": rejection_reason,
            "config_id": config_id,
        }

    # Apply edits if the user changed any fields
    if decision_type == "edit" and primary.get("args"):
        edited = primary["args"]
        if "frequency_hours" in edited:
            frequency_hours = float(edited["frequency_hours"])
            config_data["frequency_hours"] = frequency_hours
            config_data["frequency_label"] = frequency_labels.get(
                frequency_hours,
                f"Every {round(frequency_hours * 60)} min" if frequency_hours < 1 else f"Every {frequency_hours}h",
            )
        if "aspects" in edited:
            aspects = list(edited["aspects"])
            config_data["aspects"] = aspects
        if "notification_preference" in edited:
            notification_preference = edited["notification_preference"]
            config_data["notification_preference"] = notification_preference

    logger.info(f"[HITL_TOOL] 🚀 Proceeding to save config after approval")
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


@tool
async def check_user_competitors() -> dict:
    """
    Retrieve all competitors that the user is currently monitoring, with their monitoring status.
    
    USE THIS TOOL when the user:
    - Asks "what competitors am I monitoring?"
    - Wants to see their active/paused monitoring jobs
    - Asks "show me my competitors"
    - Wants to check monitoring status before making changes
    - Says: "list my monitors", "what's being tracked"
    
    This tool provides visibility into:
    - All configured competitor monitoring jobs
    - Current status (active, paused, failed)
    - Monitoring frequency and aspects
    - Last execution time and next scheduled run
    
    Returns:
        dict with:
        - total_configs: Number of monitoring configurations
        - active_count: Number of active monitors
        - paused_count: Number of paused monitors
        - competitors: List of competitor details with status
        
    Example:
        User: "What competitors am I monitoring?"
        → check_user_competitors()
        Then respond with a summary like:
        "You're currently monitoring 3 competitors:
        - Nike (active, checks every 6 hours for news and products)
        - Adidas (paused, was checking daily for pricing)
        - Puma (active, checks every 12 hours for social media)"
    """
    logger.info(f"[CHECK_COMPETITORS] 🔍 Checking user competitors for user_id: {_user_id}")
    
    if not _firestore_client:
        logger.error(f"[CHECK_COMPETITORS] ❌ No Firestore client available")
        return {
            "error": "Database not available",
            "total_configs": 0,
            "active_count": 0,
            "paused_count": 0,
            "competitors": []
        }
    
    try:
        # Query monitoring_configs for this user
        configs_query = _firestore_client.collection('monitoring_configs')
        
        if _user_id:
            configs_query = configs_query.where('user_id', '==', _user_id)
        
        configs = configs_query.stream()
        
        competitors_list = []
        active_count = 0
        paused_count = 0
        
        for config_doc in configs:
            config_data = config_doc.to_dict()
            config_id = config_doc.id
            
            # Get status
            status = config_data.get('status', 'unknown')
            
            # Skip and hard-delete stale 'deleted' documents
            if status == 'deleted':
                logger.info(f"[CHECK_COMPETITORS] Cleaning up stale deleted config: {config_id}")
                try:
                    _firestore_client.collection('monitoring_configs').document(config_id).delete()
                    logger.info(f"[CHECK_COMPETITORS] ✅ Deleted stale config {config_id} from Firestore")
                except Exception as cleanup_err:
                    logger.warning(f"[CHECK_COMPETITORS] Failed to clean up {config_id}: {cleanup_err}")
                continue
            
            if status == 'active':
                active_count += 1
            elif status == 'paused':
                paused_count += 1
            
            # Get job details from cron_jobs if available
            job_id = config_data.get('apscheduler_job_id')
            job_status = "no job"
            last_execution = None
            next_run = None
            error_count = 0
            
            if job_id:
                try:
                    job_doc = _firestore_client.collection('cron_jobs').document(job_id).get()
                    if job_doc.exists:
                        job_data = job_doc.to_dict()
                        job_status = job_data.get('status', 'unknown')
                        last_execution = job_data.get('last_execution')
                        next_run = job_data.get('next_run')
                        error_count = job_data.get('error_count', 0)
                except Exception as job_error:
                    logger.warning(f"[CHECK_COMPETITORS] Failed to get job details for {job_id}: {job_error}")
            
            # Build competitor info
            competitor_info = {
                "config_id": config_id,
                "competitor": config_data.get('competitor', 'Unknown'),
                "aspects": config_data.get('aspects', []),
                "frequency_hours": config_data.get('frequency_hours', 24),
                "frequency_label": config_data.get('frequency_label', 'Unknown'),
                "status": status,
                "job_id": job_id,
                "job_status": job_status,
                "notification_preference": config_data.get('notification_preference', 'significant_only'),
                "created_at": config_data.get('created_at'),
                "updated_at": config_data.get('updated_at'),
                "last_execution": last_execution,
                "next_run": next_run,
                "error_count": error_count,
            }
            
            competitors_list.append(competitor_info)
        
        # Sort by created_at (most recent first)
        competitors_list.sort(key=lambda x: x.get('created_at') or '', reverse=True)
        
        result = {
            "total_configs": len(competitors_list),
            "active_count": active_count,
            "paused_count": paused_count,
            "competitors": competitors_list
        }
        
        logger.info(f"[CHECK_COMPETITORS] ✅ Found {len(competitors_list)} competitors (active: {active_count}, paused: {paused_count})")
        return result
        
    except Exception as e:
        logger.error(f"[CHECK_COMPETITORS] ❌ Error checking competitors: {e}", exc_info=True)
        return {
            "error": str(e),
            "total_configs": 0,
            "active_count": 0,
            "paused_count": 0,
            "competitors": []
        }


@tool
async def update_monitoring_config(
    config_id: str,
    competitor: Optional[str] = None,
    aspects: Optional[List[str]] = None,
    frequency_hours: Optional[float] = None,
    notification_preference: Optional[str] = None,
    action: Optional[str] = None,
) -> dict:
    """
    Update an existing monitoring configuration with human-in-the-loop approval.
    
    USE THIS TOOL when the user wants to:
    - Change monitoring frequency ("check Nike every hour instead")
    - Add/remove monitoring aspects ("stop tracking pricing, add social media")
    - Change notification settings ("notify me always" or "only for important changes")
    - Pause or resume monitoring ("pause Nike monitoring", "resume Adidas tracking")
    - Change competitor name ("rename monitor to 'Nike Inc'")
    - Delete monitoring configuration ("delete Nike monitoring", "stop tracking Adidas")
    
    IMPORTANT: This tool handles HITL approval internally via LangGraph interrupt().
    The graph pauses for user approval BEFORE this tool returns any result.
    When this tool returns (status: 'updated' or 'deleted'), approval has ALREADY been
    granted and the change is LIVE. Generate a confirmation message immediately — do NOT
    ask the user to approve again.

    Args:
        config_id: The configuration ID to update (get from check_user_competitors)
        competitor: New competitor name (optional, only if renaming)
        aspects: New list of aspects to monitor (optional).
                 Choose from: ["products", "pricing", "news", "social"]
                 If provided, replaces current aspects entirely.
        frequency_hours: New monitoring frequency in hours (optional).
                 Common values: 1.0, 6.0, 12.0, 24.0
        notification_preference: New notification setting (optional).
                 Options: "significant_only", "always", "never"
        action: Special action to perform (optional).
                Options: "pause" (pause monitoring), "resume" (resume monitoring), "delete" (delete monitoring config and job)
    
    Returns:
        dict with:
        - config_id: Configuration identifier
        - status: Updated status
        - changes: Summary of what changed
        - previous_values: What the settings were before
        - new_values: What the settings are now
        
    Example:
        User: "Change Nike monitoring to check every 2 hours"
        First call check_user_competitors to get config_id
        Then: update_monitoring_config(config_id="config_abc123", frequency_hours=2.0)
        When the tool returns → immediately say: "✅ Nike monitoring updated! Now checks every 2 hours."
        
        User: "Delete the Adidas monitoring"
        First call check_user_competitors to get config_id
        Then: update_monitoring_config(config_id="config_xyz789", action="delete")
        When the tool returns → immediately say: "✅ Adidas monitoring deleted."
    """
    logger.info(f"[UPDATE_CONFIG] 🔧 update_monitoring_config CALLED")
    logger.info(f"[UPDATE_CONFIG] config_id: {config_id}, action: {action}")
    logger.info(f"[UPDATE_CONFIG] Updates - competitor: {competitor}, aspects: {aspects}, frequency: {frequency_hours}, notification: {notification_preference}")
    logger.info(f"[UPDATE_CONFIG] ⚠️ This tool should trigger HITL approval flow")
    
    if not _firestore_client:
        logger.error(f"[UPDATE_CONFIG] ❌ No Firestore client available")
        return {
            "error": "Database not available",
            "config_id": config_id
        }
    
    if not _cron_service:
        logger.error(f"[UPDATE_CONFIG] ❌ No CronService available")
        return {
            "error": "CronService not available",
            "config_id": config_id
        }
    
    try:
        # Get current config
        config_doc = _firestore_client.collection('monitoring_configs').document(config_id).get()
        
        if not config_doc.exists:
            logger.error(f"[UPDATE_CONFIG] ❌ Config {config_id} not found")
            return {
                "error": f"Configuration {config_id} not found",
                "config_id": config_id
            }
        
        current_config = config_doc.to_dict()
        logger.info(f"[UPDATE_CONFIG] Current config retrieved: {current_config.get('competitor')}")

        # ── Human-in-the-Loop approval (per LangGraph interrupt() pattern) ──────
        # Build a human-readable proposal so the user can review before any changes
        # are applied.  interrupt() pauses here; on resume it returns the decision.
        proposed_args = {
            "config_id": config_id,
            "competitor": current_config.get("competitor"),
            "current_frequency": current_config.get("frequency_label"),
            "current_aspects": current_config.get("aspects"),
            "current_status": current_config.get("status"),
        }
        if action:
            proposed_args["action"] = action
        if frequency_hours is not None:
            proposed_args["new_frequency_hours"] = frequency_hours
            proposed_args["new_frequency_label"] = {
                1: "Every hour", 2: "Every 2 hours", 6: "Every 6 hours",
                12: "Twice daily", 24: "Daily",
            }.get(frequency_hours, f"Every {frequency_hours}h")
        if aspects is not None:
            proposed_args["new_aspects"] = aspects
        if notification_preference is not None:
            proposed_args["new_notification_preference"] = notification_preference
        if competitor is not None:
            proposed_args["new_competitor_name"] = competitor

        action_label = {
            "pause": "Pause", "resume": "Resume", "delete": "Delete"
        }.get((action or "").lower(), "Update")
        proposal = {
            "action_requests": [{
                "name": "update_monitoring_config",
                "action": "update_monitoring_config",
                "arguments": proposed_args,
                "args": proposed_args,
                "description": (
                    f"{action_label} monitoring config for **{current_config.get('competitor', 'Unknown')}** "
                    f"(config_id: {config_id}). Review the proposed changes below."
                ),
            }],
            "review_configs": [{
                "action_name": "update_monitoring_config",
                "allowed_decisions": ["approve", "edit", "reject"],
            }],
        }
        logger.info(f"[UPDATE_CONFIG] ⏳ Waiting for HITL approval (update_monitoring_config)...")
        decision_value = lg_interrupt(proposal)
        logger.info(f"[UPDATE_CONFIG] ✅ HITL resumed with: {decision_value}")

        # Parse decision
        decisions_list = decision_value.get("decisions", []) if isinstance(decision_value, dict) else []
        primary = decisions_list[0] if decisions_list else {"type": "approve"}
        decision_type = primary.get("type", "approve")

        if decision_type == "reject":
            rejection_reason = primary.get("feedback") or primary.get("reason") or ""
            logger.info(f"[UPDATE_CONFIG] ❌ update_monitoring_config rejected by user. Reason: {rejection_reason}")
            competitor_name = current_config.get('competitor', 'Unknown')
            rejection_message = f"Configuration update for {competitor_name} was rejected."
            if rejection_reason:
                rejection_message += f" User's reason: {rejection_reason}"
            return {
                "status": "rejected",
                "message": rejection_message,
                "rejection_reason": rejection_reason,
                "config_id": config_id,
            }

        # Apply edits if user changed any fields
        if decision_type == "edit" and primary.get("args"):
            edited = primary["args"]
            if "new_frequency_hours" in edited and frequency_hours is None:
                frequency_hours = float(edited["new_frequency_hours"])
            elif "frequency_hours" in edited and frequency_hours is None:
                frequency_hours = float(edited["frequency_hours"])
            if "new_aspects" in edited and aspects is None:
                aspects = list(edited["new_aspects"])
            elif "aspects" in edited and aspects is None:
                aspects = list(edited["aspects"])
            if "new_notification_preference" in edited and notification_preference is None:
                notification_preference = edited["new_notification_preference"]
            elif "notification_preference" in edited and notification_preference is None:
                notification_preference = edited["notification_preference"]

        logger.info(f"[UPDATE_CONFIG] 🚀 Proceeding to apply updates after approval")
        # Track what's changing
        changes = []
        previous_values = {}
        new_values = {}
        
        # Handle special actions (pause/resume/delete)
        if action:
            action = action.lower()
            if action == "pause":
                job_id = current_config.get('apscheduler_job_id')
                if job_id:
                    logger.info(f"[UPDATE_CONFIG] Pausing job: {job_id}")
                    await _cron_service.pause_job(job_id)
                    changes.append("paused monitoring")
                    previous_values["status"] = current_config.get('status', 'unknown')
                    new_values["status"] = "paused"
                else:
                    logger.warning(f"[UPDATE_CONFIG] No job_id found for config {config_id}")
                    return {
                        "error": "No active job found to pause",
                        "config_id": config_id
                    }
            
            elif action == "resume":
                job_id = current_config.get('apscheduler_job_id')
                if job_id:
                    logger.info(f"[UPDATE_CONFIG] Resuming job: {job_id}")
                    await _cron_service.resume_job(job_id)
                    changes.append("resumed monitoring")
                    previous_values["status"] = current_config.get('status', 'unknown')
                    new_values["status"] = "active"
                else:
                    logger.warning(f"[UPDATE_CONFIG] No job_id found for config {config_id}")
                    return {
                        "error": "No job found to resume",
                        "config_id": config_id
                    }
            
            elif action == "delete":
                job_id = current_config.get('apscheduler_job_id')
                competitor_name = current_config.get('competitor', 'Unknown')
                
                # Delete the cron job first
                if job_id:
                    logger.info(f"[UPDATE_CONFIG] Deleting job: {job_id}")
                    try:
                        await _cron_service.delete_job(job_id)
                        logger.info(f"[UPDATE_CONFIG] ✅ Job {job_id} deleted")
                    except Exception as job_error:
                        logger.error(f"[UPDATE_CONFIG] Failed to delete job {job_id}: {job_error}")
                        return {
                            "error": f"Failed to delete job: {str(job_error)}",
                            "config_id": config_id
                        }
                else:
                    logger.warning(f"[UPDATE_CONFIG] No job_id found, proceeding to delete config only")
                
                # Delete the monitoring config from Firestore
                try:
                    _firestore_client.collection('monitoring_configs').document(config_id).delete()
                    logger.info(f"[UPDATE_CONFIG] ✅ Config {config_id} deleted from Firestore")
                except Exception as config_error:
                    logger.error(f"[UPDATE_CONFIG] Failed to delete config {config_id}: {config_error}")
                    return {
                        "error": f"Failed to delete configuration: {str(config_error)}",
                        "config_id": config_id
                    }
                
                return {
                    "config_id": config_id,
                    "status": "deleted",
                    "competitor": competitor_name,
                    "message": f"Monitoring configuration for {competitor_name} has been deleted.",
                    "job_deleted": job_id is not None,
                    "job_id": job_id
                }
        
        # Build update payload for CronService
        job_updates = {}
        config_updates = {
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Update competitor name
        if competitor is not None and competitor != current_config.get('competitor'):
            changes.append(f"competitor name: '{current_config.get('competitor')}' → '{competitor}'")
            previous_values["competitor"] = current_config.get('competitor')
            new_values["competitor"] = competitor
            config_updates['competitor'] = competitor
        
        # Update aspects
        if aspects is not None:
            current_aspects = current_config.get('aspects', [])
            if set(aspects) != set(current_aspects):
                changes.append(f"aspects: {current_aspects} → {aspects}")
                previous_values["aspects"] = current_aspects
                new_values["aspects"] = aspects
                config_updates['aspects'] = aspects
                job_updates['aspects'] = aspects
        
        # Update frequency
        if frequency_hours is not None:
            current_freq = current_config.get('frequency_hours', 24)
            if frequency_hours != current_freq:
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
                
                new_label = frequency_labels.get(
                    frequency_hours,
                    f"Every {round(frequency_hours * 60)} min"
                    if frequency_hours < 1
                    else f"Every {frequency_hours}h"
                )
                
                changes.append(f"frequency: {current_config.get('frequency_label', 'Unknown')} → {new_label}")
                previous_values["frequency_hours"] = current_freq
                previous_values["frequency_label"] = current_config.get('frequency_label', 'Unknown')
                new_values["frequency_hours"] = frequency_hours
                new_values["frequency_label"] = new_label
                
                config_updates['frequency_hours'] = frequency_hours
                config_updates['frequency_label'] = new_label
                job_updates['frequency_hours'] = frequency_hours
        
        # Update notification preference
        if notification_preference is not None:
            current_notif = current_config.get('notification_preference', 'significant_only')
            if notification_preference != current_notif:
                changes.append(f"notifications: {current_notif} → {notification_preference}")
                previous_values["notification_preference"] = current_notif
                new_values["notification_preference"] = notification_preference
                config_updates['notification_preference'] = notification_preference
                job_updates['notification_preference'] = notification_preference
        
        # If no changes, return early
        if not changes:
            logger.info(f"[UPDATE_CONFIG] No changes detected for config {config_id}")
            return {
                "config_id": config_id,
                "status": "no_changes",
                "message": "No changes detected. Configuration remains the same.",
                "current_config": current_config
            }
        
        # Apply updates to Firestore
        logger.info(f"[UPDATE_CONFIG] Applying {len(changes)} changes to config {config_id}")
        _firestore_client.collection('monitoring_configs').document(config_id).update(config_updates)
        
        # Apply job updates if there are any
        if job_updates:
            job_id = current_config.get('apscheduler_job_id')
            if job_id:
                logger.info(f"[UPDATE_CONFIG] Updating job {job_id} with: {job_updates}")
                await _cron_service.update_job(job_id, job_updates)
            else:
                logger.warning(f"[UPDATE_CONFIG] No job_id found, skipping job updates")
        
        # Get updated config
        updated_doc = _firestore_client.collection('monitoring_configs').document(config_id).get()
        updated_config = updated_doc.to_dict() if updated_doc.exists else current_config
        
        result = {
            "config_id": config_id,
            "status": "updated",
            "competitor": updated_config.get('competitor'),
            "changes": changes,
            "previous_values": previous_values,
            "new_values": new_values,
            "current_config": updated_config
        }
        
        logger.info(f"[UPDATE_CONFIG] ✅ Configuration updated successfully: {changes}")
        return result
        
    except GraphInterrupt:
        # Must re-raise so GraphInterrupt propagates through the agent
        # framework and surfaces as a proper HITL interrupt event.
        # Without this, the except Exception block below would catch it
        # and serialize it as an error string, silently swallowing the HITL.
        raise
    except Exception as e:
        logger.error(f"[UPDATE_CONFIG] ❌ Error updating config {config_id}: {e}", exc_info=True)
        return {
            "error": str(e),
            "config_id": config_id
        }
