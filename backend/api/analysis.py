"""
Job Analysis API Endpoints

Main endpoints for the 7-step job application analysis workflow.
Provides job analysis, progress tracking, and result retrieval.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse

from services.job_analysis_service import (
    get_job_analysis_service,
    JobAnalysisService,
    JobAnalysisError,
    AnalysisResult
)
from services.auth_service import SessionData
from api.middleware import jwt_bearer
from api.models import (
    JobAnalysisRequest,
    JobAnalysisResponse,
    ProgressResponse,
    AnalysisResults,
    ProcessingStatusEnum,
    ErrorResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["job-analysis"])


@router.post("/analyze-application", response_model=JobAnalysisResponse)
async def analyze_application(
    job_description: str = Form(..., description="Job posting description"),
    job_url: Optional[str] = Form(None, description="Optional job posting URL"),
    company_name: Optional[str] = Form(None, description="Company name for targeted research"),
    resume_text: Optional[str] = Form(None, description="Resume text content"),
    resume_file: Optional[UploadFile] = File(None, description="Resume file upload"),
    tone: str = Form("professional", description="Cover letter tone"),
    focus_areas: str = Form("technical skills,relevant experience", description="Comma-separated focus areas"),
    include_salary_guidance: bool = Form(False, description="Include salary negotiation tips"),
    include_interview_prep: bool = Form(False, description="Include interview preparation")
) -> JobAnalysisResponse:
    """
    Start comprehensive job application analysis.
    
    Initiates the 7-step analysis workflow:
    1. Job Description Analysis (14%)
    2. Company Research (28%)
    3. Resume Parsing (42%)
    4. Skills Gap Analysis (57%)
    5. Resume Enhancement (71%)
    6. Cover Letter Generation (85%)
    7. Final Review & Formatting (100%)
    
    Either resume_text or resume_file must be provided.
    """
    try:
        job_analysis_service = get_job_analysis_service()
        
        # Validate inputs
        if not job_description or len(job_description.strip()) < 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job description must be at least 50 characters long"
            )
        
        # Handle resume input
        resume_content = None
        resume_file_id = None
        
        if resume_file:
            # Read uploaded file
            try:
                file_content = await resume_file.read()
                resume_content = file_content.decode('utf-8')
                resume_file_id = f"uploaded_{resume_file.filename}"
            except Exception as e:
                logger.error(f"Failed to read uploaded file: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to read uploaded file"
                )
        elif resume_text:
            resume_content = resume_text
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either resume_text or resume_file must be provided"
            )
        
        if not resume_content or len(resume_content.strip()) < 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume content must be at least 100 characters long"
            )
        
        # Parse focus areas
        focus_areas_list = [area.strip() for area in focus_areas.split(",") if area.strip()]
        
        # Prepare preferences
        preferences = {
            "tone": tone,
            "focus_areas": focus_areas_list,
            "include_salary_guidance": include_salary_guidance,
            "include_interview_prep": include_interview_prep
        }
        
        # Start analysis (create a temporary session for now)
        from services.auth_service import SessionData
        import uuid
        
        # Create temporary session for HMAC-only authentication
        temp_session = SessionData(
            session_id=str(uuid.uuid4()),
            user_id="hmac_user",
            permissions=["analyze"]
        )
        
        analysis_id = await job_analysis_service.start_analysis(
            session_data=temp_session,
            job_description=job_description,
            job_url=job_url,
            company_name=company_name,
            resume_file_id=resume_file_id,
            resume_text=resume_content,
            preferences=preferences
        )
        
        logger.info(f"Started analysis {analysis_id} for HMAC session {temp_session.session_id}")
        
        # Get initial progress
        progress = job_analysis_service.get_progress(analysis_id)
        
        return JobAnalysisResponse(
            session_id=analysis_id,
            status=ProcessingStatusEnum.PROCESSING,
            progress=progress or {},
            estimated_completion=None  # Will be calculated based on current load
        )
        
    except JobAnalysisError as e:
        logger.error(f"Job analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze_application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during analysis startup"
        )


@router.get("/analysis/{analysis_id}/progress", response_model=Dict[str, Any])
async def get_analysis_progress(
    analysis_id: str
) -> Dict[str, Any]:
    """
    Get real-time progress for a job analysis.
    
    Returns current step, overall progress percentage, and step details.
    """
    try:
        job_analysis_service = get_job_analysis_service()
        
        progress = job_analysis_service.get_progress(analysis_id)
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis {analysis_id} not found"
            )
        
        # Note: User ownership validation removed for HMAC-only authentication
        # In a production system with user management, this would validate user ownership
        
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting progress for {analysis_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analysis progress"
        )


@router.get("/analysis/{analysis_id}/results", response_model=Dict[str, Any])
async def get_analysis_results(
    analysis_id: str
) -> Dict[str, Any]:
    """
    Get completed analysis results.
    
    Returns comprehensive analysis including job analysis, company research,
    resume recommendations, cover letter, and final summary.
    """
    try:
        job_analysis_service = get_job_analysis_service()
        
        # Check if analysis exists and is completed
        progress = job_analysis_service.get_progress(analysis_id)
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis {analysis_id} not found"
            )
        
        if progress["status"] != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Analysis {analysis_id} is not yet completed. Current status: {progress['status']}"
            )
        
        # Get results
        result = job_analysis_service.get_result(analysis_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Results for analysis {analysis_id} not found"
            )
        
        # Note: User ownership validation removed for HMAC-only authentication
        # In a production system with user management, this would validate user ownership
        
        # Convert result to dictionary for JSON response
        return {
            "analysis_id": analysis_id,
            "session_id": result.session_id,
            "completed_at": result.completed_at.isoformat() if result.completed_at else None,
            "processing_time": result.processing_metadata.get("total_processing_time", 0),
            "job_analysis": result.job_analysis,
            "company_research": result.company_research,
            "parsed_resume": result.parsed_resume,
            "skills_analysis": result.skills_analysis,
            "resume_recommendations": result.resume_recommendations,
            "cover_letter": result.cover_letter,
            "final_summary": result.final_summary,
            "metadata": result.processing_metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting results for {analysis_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analysis results"
        )


@router.post("/analysis/{analysis_id}/cancel")
async def cancel_analysis(
    analysis_id: str
) -> Dict[str, str]:
    """
    Cancel a running analysis job.
    
    Stops processing and marks the analysis as cancelled.
    """
    try:
        job_analysis_service = get_job_analysis_service()
        
        # Note: User ownership validation removed for HMAC-only authentication
        # In a production system with user management, this would validate user ownership
        
        success = job_analysis_service.cancel_analysis(analysis_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel analysis {analysis_id}. It may not exist or is already completed."
            )
        
        logger.info(f"Analysis {analysis_id} cancelled")
        
        return {
            "message": f"Analysis {analysis_id} has been cancelled",
            "status": "cancelled"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling analysis {analysis_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel analysis"
        )


@router.get("/analysis/history")
async def get_analysis_history(
    limit: int = 10,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Get analysis history for the current user.
    
    Returns list of past analyses with basic information.
    """
    try:
        job_analysis_service = get_job_analysis_service()
        
        # Return all jobs for HMAC-only authentication
        # In a production system with user management, this would filter by user_id
        all_jobs = []
        for analysis_id, job_data in job_analysis_service.active_jobs.items():
            progress = job_analysis_service.get_progress(analysis_id)
            if progress:
                job_info = {
                    "analysis_id": analysis_id,
                    "status": progress["status"],
                    "overall_progress": progress["overall_progress"],
                    "started_at": progress["started_at"],
                    "updated_at": progress["updated_at"]
                }
                
                # Add job details if available
                request = job_data.get("request")
                if request:
                    job_info.update({
                        "job_description_preview": request.job_description[:100] + "..." if len(request.job_description) > 100 else request.job_description,
                        "job_url": request.job_url,
                        "preferences": request.preferences
                    })
                
                all_jobs.append(job_info)
        
        # Sort by started_at (most recent first)
        all_jobs.sort(key=lambda x: x["started_at"], reverse=True)
        
        # Apply pagination
        paginated_jobs = all_jobs[offset:offset + limit]
        
        return {
            "analyses": paginated_jobs,
            "total": len(all_jobs),
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < len(all_jobs)
        }
        
    except Exception as e:
        logger.error(f"Error getting analysis history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analysis history"
        )


@router.post("/analysis/cleanup")
async def cleanup_old_analyses(
    max_age_hours: int = 24,
    session: SessionData = Depends(jwt_bearer)
) -> Dict[str, Any]:
    """
    Clean up old completed analyses.
    
    Admin endpoint for maintenance. Removes analyses older than specified hours.
    """
    try:
        # Check for admin permissions
        if "admin" not in session.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required"
            )
        
        job_analysis_service = get_job_analysis_service()
        cleaned_count = job_analysis_service.cleanup_old_jobs(max_age_hours)
        
        logger.info(f"Cleaned up {cleaned_count} old analyses (session: {session.session_id})")
        
        return {
            "message": f"Cleaned up {cleaned_count} old analyses",
            "cleaned_analyses": cleaned_count,
            "max_age_hours": max_age_hours
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during analysis cleanup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis cleanup failed"
        )


# Health check for analysis service
@router.get("/analysis/health")
async def analysis_service_health() -> Dict[str, Any]:
    """
    Health check for job analysis service.
    """
    try:
        job_analysis_service = get_job_analysis_service()
        
        # Count active jobs by status
        status_counts = {}
        for job_data in job_analysis_service.active_jobs.values():
            job_status = str(job_data.get("status", "unknown"))
            status_counts[job_status] = status_counts.get(job_status, 0) + 1
        
        # Calculate service load
        total_jobs = len(job_analysis_service.active_jobs)
        processing_jobs = status_counts.get("AnalysisStatus.PROCESSING", 0)
        
        service_status = "healthy"
        if processing_jobs > 10:
            service_status = "busy"
        elif processing_jobs > 20:
            service_status = "overloaded"
        
        return {
            "status": service_status,
            "service": "Job Analysis Service",
            "active_jobs": total_jobs,
            "processing_jobs": processing_jobs,
            "job_status_breakdown": status_counts,
            "steps_configured": len(job_analysis_service.STEP_CONFIG),
            "dependencies": {
                "claude_service": "available",
                "file_service": "available",
                "resume_parser": "available"
            }
        }
        
    except Exception as e:
        logger.error(f"Analysis service health check failed: {e}")
        return {
            "status": "error",
            "service": "Job Analysis Service",
            "error": str(e)
        }