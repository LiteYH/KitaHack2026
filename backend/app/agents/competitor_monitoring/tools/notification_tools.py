"""
Notification tools for sending emails and alerts to users.

Enables agents to send email notifications directly to logged-in users.
"""
import logging
from typing import Annotated, Literal, Optional
from datetime import datetime

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class SendEmailInput(BaseModel):
    """Input schema for sending email notifications."""
    
    user_id: str = Field(
        description="Firebase user ID of the recipient. Use the logged-in user's ID from context."
    )
    subject: str = Field(
        description="Email subject line. Keep clear and concise (max 100 chars).",
        max_length=100
    )
    message: str = Field(
        description="Email message body. Can include HTML formatting. Be clear and actionable.",
        max_length=5000
    )
    notification_type: Literal["alert", "report", "insight", "update", "general"] = Field(
        default="general",
        description="Type of notification for categorization and styling."
    )
    priority: Literal["high", "normal", "low"] = Field(
        default="normal",
        description="Priority level affects email styling and user attention."
    )
    additional_data: Optional[dict] = Field(
        default=None,
        description="Optional metadata for logging and tracking purposes."
    )


@tool("send_email_notification", args_schema=SendEmailInput)
async def send_email_notification(
    user_id: Annotated[str, "Firebase user ID of the recipient"],
    subject: Annotated[str, "Email subject line (max 100 chars)"],
    message: Annotated[str, "Email message body (HTML supported, max 5000 chars)"],
    notification_type: Annotated[
        Literal["alert", "report", "insight", "update", "general"],
        "Type of notification"
    ] = "general",
    priority: Annotated[
        Literal["high", "normal", "low"],
        "Priority level for styling"
    ] = "normal",
    additional_data: Optional[dict] = None
) -> dict:
    """
    Send an email notification to a logged-in user.
    
    **Use cases:**
    - Send alerts about significant competitor changes
    - Share detailed analysis reports
    - Notify about completed monitoring jobs
    - Send weekly/daily digest summaries
    - Alert on HITL approval requests
    
    **Best practices:**
    - Use clear, actionable subject lines
    - Keep messages concise and scannable
    - Include relevant data and links
    - Set appropriate priority levels
    - Use notification_type for proper categorization
    
    **Examples:**
    ```
    # Alert about competitor price change
    send_email_notification(
        user_id="abc123",
        subject="🚨 Nike dropped prices by 15%",
        message="<h2>Significant Price Drop Detected</h2><p>Nike reduced prices across 12 product lines...</p>",
        notification_type="alert",
        priority="high"
    )
    
    # Send weekly digest
    send_email_notification(
        user_id="abc123",
        subject="📊 Your Weekly Competitor Digest",
        message="<h2>Week of Feb 15, 2026</h2><ul><li>3 new products launched...</li></ul>",
        notification_type="report",
        priority="normal"
    )
    ```
    
    Args:
        user_id: Firebase user ID (from auth context)
        subject: Email subject (max 100 chars)
        message: Email body (HTML supported, max 5000 chars)
        notification_type: Category of notification
        priority: Priority level for user attention
        additional_data: Optional metadata
        
    Returns:
        dict: {
            "success": bool,
            "message": str,
            "email_sent_to": str (if successful),
            "notification_id": str (if logged)
        }
    """
    try:
        logger.info(f"[SEND_EMAIL_TOOL] Sending {notification_type} email to user {user_id}")
        
        # Initialize notification service
        notification_service = NotificationService()
        
        # Send email via service
        result = await notification_service.send_email(
            user_id=user_id,
            subject=subject,
            message=message,
            notification_type=notification_type,
            priority=priority,
            additional_data=additional_data or {}
        )
        
        if result.get("success"):
            logger.info(f"[SEND_EMAIL_TOOL] ✅ Email sent successfully to {result.get('email')}")
            return {
                "success": True,
                "message": f"Email sent successfully to {result.get('email')}",
                "email_sent_to": result.get("email"),
                "notification_id": result.get("notification_id")
            }
        else:
            logger.warning(f"[SEND_EMAIL_TOOL] ⚠️ Failed to send email: {result.get('error')}")
            return {
                "success": False,
                "message": f"Failed to send email: {result.get('error', 'Unknown error')}",
                "error": result.get("error")
            }
            
    except Exception as e:
        logger.error(f"[SEND_EMAIL_TOOL] ❌ Error sending email: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Error sending email: {str(e)}",
            "error": str(e)
        }


# Export tools for agent registration
__all__ = ["send_email_notification"]
