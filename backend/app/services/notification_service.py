"""
Notification Service for sending monitoring alerts via email.

Uses Gmail API to send notifications about significant competitor changes.
"""
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# For now, we'll use SMTP as a simpler alternative to Gmail API
# Gmail API requires OAuth2 setup which is more complex
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.cloud import firestore
from jinja2 import Template

from app.core.config import settings
from app.core.firebase import get_db

logger = logging.getLogger(__name__)

# Path to email templates
TEMPLATES_DIR = Path(__file__).parent.parent / "agents" / "competitor_monitoring" / "skills" / "notification_management" / "email_templates"


class NotificationService:
    """
    Service for sending email notifications about monitoring results.
    
    Currently uses SMTP for simplicity. Can be upgraded to Gmail API
    with OAuth2 for production use.
    """
    
    def __init__(self):
        self.firestore = get_db()
        self.smtp_enabled = self._check_smtp_config()
    
    def _check_smtp_config(self) -> bool:
        """Check if SMTP is configured"""
        # Check for SMTP environment variables
        smtp_host = os.getenv('SMTP_HOST')
        smtp_user = os.getenv('SMTP_USER')
        smtp_pass = os.getenv('SMTP_PASSWORD')
        
        if smtp_host and smtp_user and smtp_pass:
            logger.info("SMTP configuration found")
            return True
        else:
            logger.warning("SMTP not configured - notifications will be logged only")
            return False
    
    async def send_monitoring_notification(
        self,
        user_id: str,
        competitor: str,
        findings: Dict[str, Any],
        summary: str,
        significance_score: int,
        reasons: List[str]
    ) -> bool:
        """
        Send a notification about monitoring results.
        
        Args:
            user_id: User ID to send notification to
            competitor: Competitor name
            findings: Raw findings data
            summary: Summary text
            significance_score: Significance score (0-100)
            reasons: List of significance reasons
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            # Get user's email from Firestore
            user_email = await self._get_user_email(user_id)
            
            if not user_email:
                logger.warning(f"No email found for user {user_id}")
                return False
            
            # Render email template
            email_html = self._render_email_template(
                competitor=competitor,
                findings=findings,
                significance_score=significance_score,
                reasons=reasons,
                summary=summary
            )
            
            # Generate subject line
            subject = self._generate_subject(competitor, significance_score)
            
            # Send email
            if self.smtp_enabled:
                success = await self._send_email(
                    to_email=user_email,
                    subject=subject,
                    html_body=email_html
                )
            else:
                # Log notification instead of sending
                logger.info(f"[NOTIFICATION] Would send to {user_email}")
                logger.info(f"[NOTIFICATION] Subject: {subject}")
                logger.info(f"[NOTIFICATION] Body preview: {summary[:200]}...")
                success = True  # Consider it successful for testing
            
            # Log the notification
            if success:
                await self._log_notification(
                    user_id=user_id,
                    competitor=competitor,
                    email=user_email,
                    significance_score=significance_score
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}", exc_info=True)
            return False
    
    async def _get_user_email(self, user_id: str) -> Optional[str]:
        """Get user's email address from Firestore"""
        try:
            # Try to get from user profile
            user_doc = await self.firestore.collection('users').document(user_id).get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                email = user_data.get('email')
                if email:
                    return email
            
            # Fallback: try to get from monitoring_configs
            configs = await self.firestore.collection('monitoring_configs').where(
                'user_id', '==', user_id
            ).limit(1).get()
            
            if configs:
                config_data = configs[0].to_dict()
                return config_data.get('notification_email')
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user email: {e}")
            return None
    
    def _render_email_template(
        self,
        competitor: str,
        findings: Dict[str, Any],
        significance_score: int,
        reasons: List[str],
        summary: str
    ) -> str:
        """
        Render the email template with monitoring data.
        
        Args:
            competitor: Competitor name
            findings: Findings data
            significance_score: Significance score
            reasons: List of reasons
            summary: Summary text
            
        Returns:
            Rendered HTML email
        """
        try:
            # Load template
            template_path = TEMPLATES_DIR / "significant_change.html"
            
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
            else:
                # Fallback to simple template
                logger.warning("Email template not found, using fallback")
                template_content = self._get_fallback_template()
            
            # Prepare template variables
            significance_level = self._get_significance_level(significance_score)
            
            # Extract news articles from findings
            news = findings.get('news', {})
            news_articles = []
            if isinstance(news, dict) and 'articles' in news:
                for article in news['articles'][:3]:  # Top 3 articles
                    news_articles.append({
                        'title': article.get('title', 'No title'),
                        'url': article.get('url', '#'),
                        'published_date': article.get('published_date', 'Unknown date')
                    })
            
            # Extract competitor updates
            competitor_info = findings.get('competitor_info', {})
            competitor_updates = []
            if isinstance(competitor_info, dict) and 'results' in competitor_info:
                for result in competitor_info['results'][:3]:  # Top 3 results
                    competitor_updates.append({
                        'title': result.get('title', 'No title'),
                        'url': result.get('url', '#'),
                        'content': result.get('content', '')[:200] + '...'  # Truncate
                    })
            
            # Render template (simplified - not using Jinja2 for now)
            html = template_content
            html = html.replace('{{ competitor }}', competitor)
            html = html.replace('{{ significance_score }}', str(significance_score))
            html = html.replace('{{ significance_level }}', significance_level)
            
            # Build reasons HTML
            reasons_html = ''.join([f'<li>{reason}</li>' for reason in reasons])
            html = html.replace('{% for reason in reasons %}<li>{{ reason }}</li>{% endfor %}', reasons_html)
            
            # Build news HTML
            if news_articles:
                news_html = ''
                for article in news_articles:
                    news_html += f'''
                    <div style="margin: 15px 0; padding: 10px; background-color: #f8fafc; border-radius: 4px;">
                        <strong><a href="{article['url']}" style="color: #2563eb; text-decoration: none;">{article['title']}</a></strong>
                        <p style="margin: 5px 0 0 0; font-size: 14px; color: #6b7280;">{article['published_date']}</p>
                    </div>
                    '''
                html = html.replace('{% if news_articles %}', '').replace('{% endif %}', '')
                html = html.replace('{% for article in news_articles %}...{% endfor %}', news_html)
            else:
                # Remove news section
                html = html.split('{% if news_articles %}')[0] + html.split('{% endif %}')[-1]
            
            # Build competitor updates HTML (similar approach)
            if competitor_updates:
                updates_html = ''
                for update in competitor_updates:
                    updates_html += f'''
                    <div style="margin: 15px 0; padding: 10px; background-color: #f8fafc; border-radius: 4px;">
                        <strong><a href="{update['url']}" style="color: #2563eb; text-decoration: none;">{update['title']}</a></strong>
                        <p style="margin: 5px 0 0 0; font-size: 14px; color: #4b5563;">{update['content']}</p>
                    </div>
                    '''
                html = html.replace('{% if competitor_updates %}', '').replace('{% endif %}', '')
                html = html.replace('{% for update in competitor_updates %}...{% endfor %}', updates_html)
            
            # Add placeholder URLs (these would be real in production)
            html = html.replace('{{ dashboard_url }}', 'http://localhost:3000/dashboard')
            html = html.replace('{{ manage_url }}', 'http://localhost:3000/settings/monitoring')
            html = html.replace('{{ unsubscribe_url }}', 'http://localhost:3000/settings/notifications')
            
            return html
            
        except Exception as e:
            logger.error(f"Error rendering email template: {e}", exc_info=True)
            # Return simple fallback
            return self._get_simple_email_body(competitor, significance_score, reasons, summary)
    
    def _get_significance_level(self, score: int) -> str:
        """Get significance level string from score"""
        if score >= 80:
            return 'critical'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        else:
            return 'low'
    
    def _get_fallback_template(self) -> str:
        """Simple fallback template"""
        return """
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h1>Competitor Monitoring Alert: {{ competitor }}</h1>
            <p><strong>Significance Score:</strong> {{ significance_score }}/100</p>
            <h2>Key Findings:</h2>
            <ul>{% for reason in reasons %}<li>{{ reason }}</li>{% endfor %}</ul>
            {% if news_articles %}<h2>Recent News:</h2>{% for article in news_articles %}...{% endfor %}{% endif %}
            {% if competitor_updates %}<h2>Competitor Updates:</h2>{% for update in competitor_updates %}...{% endfor %}{% endif %}
        </body>
        </html>
        """
    
    def _get_simple_email_body(
        self,
        competitor: str,
        significance_score: int,
        reasons: List[str],
        summary: str
    ) -> str:
        """Generate a simple text email body"""
        lines = [
            f"Competitor Monitoring Alert: {competitor}",
            "",
            f"Significance Score: {significance_score}/100",
            "",
            "Key Findings:",
        ]
        
        for reason in reasons:
            lines.append(f"- {reason}")
        
        lines.append("")
        lines.append("Summary:")
        lines.append(summary)
        
        return "\n".join(lines)
    
    def _generate_subject(self, competitor: str, significance_score: int) -> str:
        """Generate email subject line"""
        if significance_score >= 80:
            urgency = "🚨 CRITICAL"
        elif significance_score >= 60:
            urgency = "⚠️ HIGH"
        elif significance_score >= 40:
            urgency = "📊 MEDIUM"
        else:
            urgency = "ℹ️"
        
        return f"{urgency} Competitor Alert: {competitor} - Significance {significance_score}/100"
    
    async def _send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str
    ) -> bool:
        """
        Send email via SMTP.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_body: HTML email body
            
        Returns:
            True if sent successfully
        """
        try:
            smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER')
            smtp_pass = os.getenv('SMTP_PASSWORD')
            from_email = os.getenv('SMTP_FROM_EMAIL', smtp_user)
            
            if not smtp_user or not smtp_pass:
                logger.error("SMTP credentials not configured")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email
            
            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send via SMTP
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}", exc_info=True)
            return False
    
    async def _log_notification(
        self,
        user_id: str,
        competitor: str,
        email: str,
        significance_score: int
    ):
        """Log the notification to Firestore"""
        try:
            await self.firestore.collection('notification_log').add({
                'user_id': user_id,
                'competitor': competitor,
                'email': email,
                'significance_score': significance_score,
                'sent_at': firestore.SERVER_TIMESTAMP,
                'type': 'monitoring_alert'
            })
        except Exception as e:
            logger.error(f"Failed to log notification: {e}")


# Singleton instance
notification_service = NotificationService()
