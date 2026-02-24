#!/usr/bin/env python3
"""
YouTube PDF Generation Service using xhtml2pdf
Handles the agent flow: analyze YouTube ROI metrics -> generate HTML -> convert to PDF
"""

import asyncio
import os
import sys
import json
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

# Import xhtml2pdf with compatibility fix for reportlab 4.4+
try:
    # Fix for xhtml2pdf compatibility with reportlab 4.4+
    import reportlab.platypus.frames as frames
    if not hasattr(frames, 'ShowBoundaryValue'):
        frames.ShowBoundaryValue = False  # Add missing attribute
    
    from xhtml2pdf import pisa
    XHTML2PDF_AVAILABLE = True
    print("✅ xhtml2pdf available (with reportlab compatibility fix)")
except ImportError as e:
    XHTML2PDF_AVAILABLE = False
    print(f"❌ xhtml2pdf not available: {e}")

from app.services.youtube_report.youtube_ai_agent import YouTubeROIReportAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubePDFGenerator:
    """
    Main YouTube PDF generation service that orchestrates the agent flow
    """
    
    def __init__(self):
        self.xhtml2pdf_available = XHTML2PDF_AVAILABLE
        self.ai_agent = YouTubeROIReportAgent()
        
        if not self.xhtml2pdf_available:
            logger.warning("xhtml2pdf not available. PDF generation will be limited.")
    
    async def generate_youtube_report(self, user_id: Optional[str] = None, user_email: Optional[str] = None, days: Optional[int] = None) -> Dict[str, Any]:
        """
        Main method to generate YouTube ROI report:
        1. Analyze YouTube ROI metrics from Firestore
        2. Generate HTML report
        3. Convert HTML to PDF
        4. Return content for download (no server storage)
        
        Args:
            user_id: Optional user ID for filtering
            user_email: Optional user email for filtering (takes precedence)
            days: Optional number of days to filter data (e.g., last 7 days)
        """
        try:
            logger.info("🚀 Starting YouTube ROI report generation...")
            
            # Step 1: Analyze YouTube ROI metrics and generate HTML
            if days:
                logger.info(f"📊 Step 1: Analyzing YouTube metrics and generating HTML (filtered: last {days} days)...")
            else:
                logger.info("📊 Step 1: Analyzing YouTube metrics and generating HTML (all time)...")
            html_content, report_data = await self.ai_agent.generate_html_report(
                user_id=user_id, 
                user_email=user_email,
                days=days
            )
            
            if not html_content:
                raise Exception("Failed to generate HTML content")
            
            # Step 2: Convert HTML to PDF
            logger.info("📄 Step 2: Converting HTML to PDF...")
            pdf_bytes = await self.convert_html_to_pdf(html_content)
            
            if not pdf_bytes:
                logger.warning("⚠️ PDF conversion failed, will provide HTML only")
                pdf_base64 = None
            else:
                # Convert PDF bytes to base64 for JSON serialization
                pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Step 3: Extract text content
            logger.info("💾 Step 3: Preparing content for download...")
            text_content = self.extract_text_from_html(html_content)
            
            logger.info("✅ YouTube report generation completed successfully!")
            
            return {
                "success": True,
                "message": "YouTube ROI report generated successfully",
                "content": {
                    "html": html_content,
                    "pdf": pdf_base64,
                    "text": text_content,
                    "json": json.dumps(report_data, indent=2, default=str)
                },
                "filenames": {
                    "html": f"youtube_roi_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.html",
                    "pdf": f"youtube_roi_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf",
                    "text": f"youtube_roi_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
                    "json": f"youtube_roi_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
                },
                "generated_at": datetime.now().isoformat(),
                "report_data": report_data,
                "user_id": user_id
            }
            
        except Exception as e:
            logger.error(f"❌ YouTube report generation failed: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to generate YouTube report: {str(e)}",
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    async def convert_html_to_pdf(self, html_content: str) -> Optional[bytes]:
        """
        Convert HTML content to PDF using xhtml2pdf with portrait orientation
        """
        if not self.xhtml2pdf_available:
            logger.error("❌ xhtml2pdf not installed")
            return None
        
        try:
            logger.info("🔄 Converting HTML to PDF using xhtml2pdf...")
            
            # Create a BytesIO object to store the PDF
            from io import BytesIO
            pdf_buffer = BytesIO()
            
            # Convert HTML to PDF with portrait orientation
            conversion_result = pisa.CreatePDF(
                html_content,
                dest=pdf_buffer,
                encoding='utf-8',
                showBoundary=0,
                orientation='portrait'
            )
            
            if conversion_result.err:
                logger.error(f"❌ PDF conversion failed: {conversion_result.err}")
                return None
            
            # Get the PDF bytes
            pdf_bytes = pdf_buffer.getvalue()
            pdf_buffer.close()
            
            logger.info(f"✅ PDF conversion successful. Size: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"❌ PDF conversion error: {str(e)}")
            return None
    
    def extract_text_from_html(self, html_content: str) -> str:
        """
        Extract plain text from HTML content for text report
        """
        try:
            from bs4 import BeautifulSoup
            
            # Parse HTML and extract text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and clean it up
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except ImportError:
            # Fallback: simple regex-based text extraction
            import re
            text = re.sub(r'<[^>]+>', '', html_content)
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        except Exception as e:
            logger.error(f"❌ Text extraction failed: {str(e)}")
            return "Text extraction failed. Please view the HTML version."


# Standalone function for backward compatibility
async def generate_youtube_report(user_id: Optional[str] = None, user_email: Optional[str] = None, days: Optional[int] = None) -> Dict[str, Any]:
    """
    Standalone function to generate YouTube ROI report
    
    Args:
        user_id: Optional user ID for filtering
        user_email: Optional user email for filtering (takes precedence)
        days: Optional number of days to filter data (e.g., last 7 days from chat context)
    """
    try:
        pdf_generator = YouTubePDFGenerator()
        result = await pdf_generator.generate_youtube_report(user_id=user_id, user_email=user_email, days=days)
        return result
    except Exception as e:
        logger.error(f"❌ Standalone YouTube report generation failed: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to generate YouTube report: {str(e)}",
            "error": str(e)
        }


if __name__ == "__main__":
    # Test the YouTube PDF generator
    async def test():
        pdf_generator = YouTubePDFGenerator()
        result = await pdf_generator.generate_youtube_report()
        
        print(f"\n{'='*60}")
        print("YouTube Report Generation Test Results")
        print(f"{'='*60}")
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        
        if result.get('success'):
            print(f"\nGenerated Files:")
            for format_type, filename in result.get('filenames', {}).items():
                content_length = len(result.get('content', {}).get(format_type, '')) if result.get('content', {}).get(format_type) else 0
                print(f"  - {format_type.upper()}: {filename} ({content_length} chars/bytes)")
            
            print(f"\nReport Data Summary:")
            report_data = result.get('report_data', {})
            youtube_data = report_data.get('youtube_data', {})
            print(f"  - Total Videos: {youtube_data.get('totals', {}).get('total_videos', 0)}")
            print(f"  - Total Views: {youtube_data.get('totals', {}).get('total_views', 0):,}")
            print(f"  - Overall ROI: {youtube_data.get('overall_roi', 0):.2f}%")
            print(f"  - Categories: {len(youtube_data.get('content_categories', {}))}")
        else:
            print(f"Error: {result.get('error')}")
        
        print(f"{'='*60}\n")
    
    asyncio.run(test())
