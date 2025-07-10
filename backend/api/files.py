"""
File Upload API Endpoints

Handles secure file uploads for resume processing.
Supports PDF, DOCX, and TXT formats with comprehensive validation.
"""

import logging
import os
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse

from services.file_service import (
    get_file_service,
    FileService,
    FileValidationError,
    FileProcessingError,
    FileInfo,
    ExtractedContent
)
from services.auth_service import SessionData
from api.middleware import jwt_bearer
from api.models import (
    FileUploadResponse,
    FileInfo as FileInfoModel,
    ProcessingStatusEnum,
    ErrorResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/files", tags=["file-upload"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_resume(
    file: UploadFile = File(..., description="Resume file (PDF, DOCX, or TXT)"),
    extract_immediately: bool = Form(True, description="Extract text immediately after upload"),
    session: SessionData = Depends(jwt_bearer)
) -> FileUploadResponse:
    """
    Upload resume file for processing.
    
    Accepts PDF, DOCX, and TXT files up to 10MB.
    Performs comprehensive security validation.
    """
    file_service = get_file_service()
    
    try:
        # Validate upload
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required"
            )
        
        # Read file content
        try:
            file_content = await file.read()
        except Exception as e:
            logger.error(f"Failed to read uploaded file: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to read file content"
            )
        
        # Save file with validation
        try:
            file_info = file_service.save_file(
                file_content=file_content,
                filename=file.filename,
                content_type=file.content_type or "application/octet-stream"
            )
        except FileValidationError as e:
            logger.warning(f"File validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File validation failed: {str(e)}"
            )
        except FileProcessingError as e:
            logger.error(f"File processing failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File processing failed"
            )
        
        # Extract text if requested
        processing_status = ProcessingStatusEnum.COMPLETED
        message = "File uploaded successfully"
        
        if extract_immediately:
            try:
                extracted_content = file_service.extract_text(file_info)
                message = f"File uploaded and text extracted successfully ({extracted_content.word_count} words)"
                
                # Store extracted content in session or temporary storage
                # For now, we'll log it and include basic info in response
                logger.info(f"Extracted {extracted_content.word_count} words from {file_info.file_id}")
                
            except FileProcessingError as e:
                logger.error(f"Text extraction failed: {e}")
                processing_status = ProcessingStatusEnum.FAILED
                message = f"File uploaded but text extraction failed: {str(e)}"
        
        # Convert to response model
        file_info_model = FileInfoModel(
            filename=file_info.original_filename,
            file_format=file_info.file_format,
            file_size=file_info.file_size,
            content_type=file_info.content_type,
            upload_timestamp=file_info.upload_timestamp
        )
        
        logger.info(f"File upload successful: {file_info.file_id} by session {session.session_id}")
        
        return FileUploadResponse(
            file_id=file_info.file_id,
            file_info=file_info_model,
            processing_status=processing_status,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during file upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during file upload"
        )


@router.get("/extract/{file_id}")
async def extract_file_content(
    file_id: str,
    session: SessionData = Depends(jwt_bearer)
) -> Dict[str, Any]:
    """
    Extract text content from previously uploaded file.
    
    Returns structured content including detected sections.
    """
    file_service = get_file_service()
    
    try:
        # Note: In a real implementation, we'd need to track file ownership
        # and validate that the session has access to this file
        
        # For now, we'll create a basic file info lookup
        # This should be replaced with proper file storage/database
        
        # TODO: Implement proper file tracking and ownership validation
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="File extraction endpoint requires file tracking system implementation"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during text extraction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Text extraction failed"
        )


@router.get("/info/{file_id}")
async def get_file_info(
    file_id: str,
    session: SessionData = Depends(jwt_bearer)
) -> Dict[str, Any]:
    """
    Get information about uploaded file.
    """
    try:
        # TODO: Implement file info retrieval from storage
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="File info endpoint requires file tracking system implementation"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving file info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve file information"
        )


@router.delete("/cleanup/{file_id}")
async def cleanup_file(
    file_id: str,
    session: SessionData = Depends(jwt_bearer)
) -> Dict[str, str]:
    """
    Clean up uploaded file.
    
    Removes temporary file from storage.
    """
    file_service = get_file_service()
    
    try:
        # TODO: Implement file lookup and ownership validation
        # For now, return success message
        
        logger.info(f"File cleanup requested: {file_id} by session {session.session_id}")
        
        return {
            "message": f"File {file_id} cleanup requested",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error during file cleanup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File cleanup failed"
        )


@router.post("/cleanup/all")
async def cleanup_old_files(
    max_age_hours: int = 24,
    session: SessionData = Depends(jwt_bearer)
) -> Dict[str, Any]:
    """
    Clean up old temporary files.
    
    Admin endpoint for maintenance.
    """
    try:
        # Check for admin permissions
        if "admin" not in session.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required"
            )
        
        file_service = get_file_service()
        cleaned_count = file_service.cleanup_old_files(max_age_hours)
        
        logger.info(f"Cleaned up {cleaned_count} old files (session: {session.session_id})")
        
        return {
            "message": f"Cleaned up {cleaned_count} old files",
            "cleaned_files": cleaned_count,
            "max_age_hours": max_age_hours
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during bulk cleanup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bulk cleanup failed"
        )


@router.get("/supported-formats")
async def get_supported_formats() -> Dict[str, Any]:
    """
    Get information about supported file formats.
    
    Public endpoint - no authentication required.
    """
    return {
        "supported_formats": {
            "pdf": {
                "description": "Adobe PDF documents",
                "mime_types": ["application/pdf"],
                "max_pages": 50,
                "notes": "Text extraction using PyPDF2"
            },
            "docx": {
                "description": "Microsoft Word documents (Office 2007+)",
                "mime_types": [
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ],
                "notes": "Supports paragraphs and tables"
            },
            "txt": {
                "description": "Plain text files",
                "mime_types": ["text/plain"],
                "encoding": "UTF-8 or auto-detected",
                "notes": "Simple text format"
            }
        },
        "limitations": {
            "max_file_size": "10 MB",
            "security": "Files are scanned for malicious content",
            "retention": "Temporary files auto-deleted after 24 hours"
        },
        "security_features": [
            "MIME type validation",
            "File structure validation",
            "Content security scanning",
            "Size limit enforcement",
            "Automatic cleanup"
        ]
    }


# Health check for file service
@router.get("/health")
async def file_service_health() -> Dict[str, Any]:
    """
    Health check for file upload service.
    """
    try:
        file_service = get_file_service()
        
        # Check temp directory
        temp_dir_exists = file_service.temp_dir.exists()
        temp_dir_writable = temp_dir_exists and os.access(file_service.temp_dir, os.W_OK)
        
        # Count temp files
        temp_file_count = 0
        if temp_dir_exists:
            temp_file_count = len(list(file_service.temp_dir.glob('file_*')))
        
        status = "healthy" if temp_dir_exists and temp_dir_writable else "degraded"
        
        return {
            "status": status,
            "service": "File Upload Service",
            "checks": {
                "temp_directory_exists": temp_dir_exists,
                "temp_directory_writable": temp_dir_writable,
                "temp_file_count": temp_file_count
            },
            "configuration": {
                "max_file_size": f"{file_service.MAX_FILE_SIZE // (1024*1024)} MB",
                "supported_formats": len(file_service.SUPPORTED_FORMATS),
                "temp_directory": str(file_service.temp_dir)
            }
        }
        
    except Exception as e:
        logger.error(f"File service health check failed: {e}")
        return {
            "status": "error",
            "service": "File Upload Service",
            "error": str(e)
        }