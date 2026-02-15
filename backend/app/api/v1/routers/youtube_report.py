#!/usr/bin/env python3
"""
YouTube Report Router
API endpoints for generating YouTube ROI reports
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response, JSONResponse
from typing import Optional
import logging
import base64

from app.services.youtube_report import generate_youtube_report

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/youtube-report",
    tags=["YouTube Reports"],
    responses={404: {"description": "Not found"}}
)


@router.post("/generate")
async def generate_report(
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """
    Generate YouTube ROI report in multiple formats (HTML, PDF, TEXT, JSON)
    
    - **user_id**: Optional user ID to filter YouTube data
    
    Returns: JSON with HTML, PDF (base64), TEXT, and JSON content
    """
    try:
        logger.info(f"📊 Generating YouTube ROI report (user_id: {user_id or 'all'})")
        
        # Generate report using the YouTube PDF generator
        result = await generate_youtube_report(user_id=user_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "Failed to generate YouTube report")
            )
        
        logger.info("✅ YouTube report generated successfully")
        
        return JSONResponse(
            content={
                "success": True,
                "message": result.get("message"),
                "data": {
                    "html": result["content"]["html"],
                    "pdf_base64": result["content"]["pdf"],
                    "text": result["content"]["text"],
                    "json": result["content"]["json"]
                },
                "filenames": result["filenames"],
                "metadata": {
                    "generated_at": result["generated_at"],
                    "user_id": user_id,
                    "record_count": result.get("report_data", {}).get("youtube_data", {}).get("record_count", 0),
                    "total_videos": result.get("report_data", {}).get("youtube_data", {}).get("totals", {}).get("total_videos", 0),
                    "overall_roi": result.get("report_data", {}).get("youtube_data", {}).get("overall_roi", 0)
                }
            },
            status_code=200
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating YouTube report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/download/html")
async def download_html_report(
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """
    Download YouTube ROI report as HTML file
    
    - **user_id**: Optional user ID to filter YouTube data
    
    Returns: HTML file for download
    """
    try:
        logger.info(f"📄 Generating YouTube HTML report for download (user_id: {user_id or 'all'})")
        
        result = await generate_youtube_report(user_id=user_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "Failed to generate YouTube report")
            )
        
        html_content = result["content"]["html"]
        filename = result["filenames"]["html"]
        
        return Response(
            content=html_content,
            media_type="text/html",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "text/html; charset=utf-8"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error downloading YouTube HTML report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/download/pdf")
async def download_pdf_report(
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """
    Download YouTube ROI report as PDF file
    
    - **user_id**: Optional user ID to filter YouTube data
    
    Returns: PDF file for download
    """
    try:
        logger.info(f"📄 Generating YouTube PDF report for download (user_id: {user_id or 'all'})")
        
        result = await generate_youtube_report(user_id=user_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "Failed to generate YouTube report")
            )
        
        pdf_base64 = result["content"]["pdf"]
        
        if not pdf_base64:
            raise HTTPException(
                status_code=500,
                detail="PDF generation failed. Please try HTML format instead."
            )
        
        # Decode base64 PDF
        pdf_bytes = base64.b64decode(pdf_base64)
        filename = result["filenames"]["pdf"]
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "application/pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error downloading YouTube PDF report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/download/text")
async def download_text_report(
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """
    Download YouTube ROI report as plain text file
    
    - **user_id**: Optional user ID to filter YouTube data
    
    Returns: Text file for download
    """
    try:
        logger.info(f"📄 Generating YouTube text report for download (user_id: {user_id or 'all'})")
        
        result = await generate_youtube_report(user_id=user_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "Failed to generate YouTube report")
            )
        
        text_content = result["content"]["text"]
        filename = result["filenames"]["text"]
        
        return Response(
            content=text_content,
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "text/plain; charset=utf-8"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error downloading YouTube text report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/download/json")
async def download_json_report(
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """
    Download YouTube ROI data as JSON file
    
    - **user_id**: Optional user ID to filter YouTube data
    
    Returns: JSON file for download
    """
    try:
        logger.info(f"📄 Generating YouTube JSON data for download (user_id: {user_id or 'all'})")
        
        result = await generate_youtube_report(user_id=user_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "Failed to generate YouTube report")
            )
        
        json_content = result["content"]["json"]
        filename = result["filenames"]["json"]
        
        return Response(
            content=json_content,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "application/json; charset=utf-8"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error downloading YouTube JSON data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/preview")
async def preview_report(
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """
    Preview YouTube ROI report metadata without generating full report
    
    - **user_id**: Optional user ID to filter YouTube data
    
    Returns: Report metadata and summary
    """
    try:
        logger.info(f"👀 Previewing YouTube report metadata (user_id: {user_id or 'all'})")
        
        # Import firestore client to get quick stats
        from app.core.firestore_client import firestore_client
        
        # Get collection stats
        youtube_data = await firestore_client.get_youtube_roi_data(user_id=user_id, limit=1000)
        
        if not youtube_data:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "No YouTube ROI data found",
                    "data": {
                        "record_count": 0,
                        "has_data": False
                    }
                },
                status_code=200
            )
        
        # Calculate basic stats
        total_records = len(youtube_data)
        total_views = sum(int(record.get("views", 0)) for record in youtube_data)
        total_revenue = sum(float(record.get("revenue_generated", 0)) for record in youtube_data)
        total_ad_spend = sum(float(record.get("ad_spend", 0)) for record in youtube_data)
        
        overall_roi = 0
        if total_ad_spend > 0:
            overall_roi = ((total_revenue - total_ad_spend) / total_ad_spend) * 100
        
        return JSONResponse(
            content={
                "success": True,
                "message": "YouTube report preview generated",
                "data": {
                    "record_count": total_records,
                    "has_data": True,
                    "preview": {
                        "total_views": total_views,
                        "total_revenue": total_revenue,
                        "total_ad_spend": total_ad_spend,
                        "overall_roi": round(overall_roi, 2)
                    }
                }
            },
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"❌ Error previewing YouTube report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
