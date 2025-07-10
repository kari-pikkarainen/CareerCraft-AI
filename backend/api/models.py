"""
API Models for CareerCraft AI

Pydantic models for request/response validation and serialization.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator
import re


class EnvironmentEnum(str, Enum):
    """Environment enumeration"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ProcessingStatusEnum(str, Enum):
    """Processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FileFormatEnum(str, Enum):
    """Supported file formats"""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


class ToneEnum(str, Enum):
    """Cover letter tone options"""
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    CONFIDENT = "confident"
    ENTHUSIASTIC = "enthusiastic"


# Base Models
class BaseResponse(BaseModel):
    """Base response model with common fields"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    success: bool = Field(True)


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: bool = Field(True)
    error_code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[str] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service health status")
    service: str = Field("CareerCraft AI")
    version: str = Field("1.0.0")
    environment: Optional[EnvironmentEnum] = Field(None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    checks: Dict[str, str] = Field(default_factory=dict)


class DetailedHealthResponse(HealthResponse):
    """Detailed health check response model"""
    uptime: Optional[str] = Field(None, description="Service uptime")
    configuration: Optional[Dict[str, Any]] = Field(None)
    security: Optional[Dict[str, Any]] = Field(None)
    dependencies: Optional[Dict[str, Any]] = Field(None)
    performance: Optional[Dict[str, Any]] = Field(None)


# Job Analysis Models
class JobPreferences(BaseModel):
    """User preferences for job analysis"""
    tone: ToneEnum = Field(ToneEnum.PROFESSIONAL, description="Cover letter tone")
    focus_areas: List[str] = Field(
        default_factory=list,
        description="Areas to focus on (e.g., 'technical skills', 'leadership')"
    )
    include_salary_guidance: bool = Field(False, description="Include salary negotiation tips")
    include_interview_prep: bool = Field(False, description="Include interview preparation")
    
    @validator('focus_areas')
    def validate_focus_areas(cls, v):
        """Validate focus areas"""
        if len(v) > 5:
            raise ValueError("Maximum 5 focus areas allowed")
        return [area.strip().lower() for area in v if area.strip()]


class JobAnalysisRequest(BaseModel):
    """Request model for job analysis"""
    job_description: str = Field(
        ...,
        min_length=50,
        max_length=50000,
        description="Job posting description text"
    )
    job_url: Optional[str] = Field(
        None,
        description="URL to the job posting (optional)"
    )
    preferences: JobPreferences = Field(
        default_factory=JobPreferences,
        description="Analysis preferences"
    )
    
    @validator('job_url')
    def validate_job_url(cls, v):
        """Validate job URL format"""
        if v is not None:
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            if not url_pattern.match(v):
                raise ValueError("Invalid URL format")
        return v


class JobAnalysisResponse(BaseModel):
    """Response model for job analysis submission"""
    session_id: str = Field(..., description="Unique session identifier")
    status: ProcessingStatusEnum = Field(..., description="Current processing status")
    progress: Dict[str, Any] = Field(..., description="Progress information")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")


# Progress Tracking Models
class ProgressStep(BaseModel):
    """Individual progress step information"""
    step_number: int = Field(..., ge=1, le=7, description="Step number (1-7)")
    step_name: str = Field(..., description="Step description")
    status: ProcessingStatusEnum = Field(..., description="Step status")
    progress_percentage: int = Field(..., ge=0, le=100, description="Step progress percentage")
    started_at: Optional[datetime] = Field(None, description="Step start time")
    completed_at: Optional[datetime] = Field(None, description="Step completion time")
    details: Optional[str] = Field(None, description="Step-specific details")


class ProgressResponse(BaseModel):
    """Progress tracking response model"""
    session_id: str = Field(..., description="Session identifier")
    status: ProcessingStatusEnum = Field(..., description="Overall status")
    overall_progress: int = Field(..., ge=0, le=100, description="Overall progress percentage")
    current_step: Optional[ProgressStep] = Field(None, description="Current step information")
    steps: List[ProgressStep] = Field(default_factory=list, description="All steps progress")
    estimated_time_remaining: Optional[str] = Field(None, description="Estimated time remaining")
    error_message: Optional[str] = Field(None, description="Error details if failed")
    started_at: datetime = Field(..., description="Processing start time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")


# Analysis Results Models
class SkillAnalysis(BaseModel):
    """Skill analysis information"""
    skill: str = Field(..., description="Skill name")
    required: bool = Field(..., description="Whether skill is required")
    present_in_resume: bool = Field(..., description="Whether skill is in resume")
    proficiency_level: Optional[str] = Field(None, description="Required proficiency level")
    importance_score: float = Field(..., ge=0, le=1, description="Importance score (0-1)")


class JobRequirement(BaseModel):
    """Job requirement information"""
    requirement: str = Field(..., description="Requirement description")
    category: str = Field(..., description="Requirement category (e.g., 'technical', 'soft_skills')")
    priority: str = Field(..., description="Priority level (required, preferred, nice-to-have)")
    matches_resume: bool = Field(..., description="Whether requirement matches resume")


class JobAnalysisResult(BaseModel):
    """Job analysis results"""
    job_title: str = Field(..., description="Extracted job title")
    company_name: Optional[str] = Field(None, description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    employment_type: Optional[str] = Field(None, description="Employment type (full-time, part-time, etc.)")
    experience_level: Optional[str] = Field(None, description="Required experience level")
    salary_range: Optional[str] = Field(None, description="Salary range if mentioned")
    
    requirements: List[JobRequirement] = Field(default_factory=list)
    skills_analysis: List[SkillAnalysis] = Field(default_factory=list)
    
    key_keywords: List[str] = Field(default_factory=list, description="Important keywords")
    industry: Optional[str] = Field(None, description="Industry/sector")
    remote_friendly: Optional[bool] = Field(None, description="Remote work allowed")
    
    analysis_score: float = Field(..., ge=0, le=1, description="Overall analysis confidence")


class CompanyInsight(BaseModel):
    """Company research insight"""
    category: str = Field(..., description="Insight category")
    title: str = Field(..., description="Insight title")
    content: str = Field(..., description="Insight content")
    source: Optional[str] = Field(None, description="Information source")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance score")


class CompanyResearchResult(BaseModel):
    """Company research results"""
    company_name: str = Field(..., description="Company name")
    industry: Optional[str] = Field(None, description="Company industry")
    size: Optional[str] = Field(None, description="Company size")
    location: Optional[str] = Field(None, description="Company location/headquarters")
    website: Optional[str] = Field(None, description="Company website")
    
    mission_statement: Optional[str] = Field(None, description="Company mission")
    values: List[str] = Field(default_factory=list, description="Company values")
    culture_keywords: List[str] = Field(default_factory=list, description="Culture-related keywords")
    
    recent_news: List[str] = Field(default_factory=list, description="Recent company news")
    insights: List[CompanyInsight] = Field(default_factory=list, description="Research insights")
    
    research_score: float = Field(..., ge=0, le=1, description="Research completeness score")


class ResumeRecommendation(BaseModel):
    """Resume improvement recommendation"""
    category: str = Field(..., description="Recommendation category")
    priority: str = Field(..., description="Priority level (high, medium, low)")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed recommendation")
    specific_examples: List[str] = Field(default_factory=list, description="Specific examples")
    keywords_to_add: List[str] = Field(default_factory=list, description="Keywords to add")


class ResumeAnalysisResult(BaseModel):
    """Resume analysis and recommendations"""
    overall_score: float = Field(..., ge=0, le=1, description="Overall resume score")
    job_match_score: float = Field(..., ge=0, le=1, description="Job match score")
    
    strengths: List[str] = Field(default_factory=list, description="Resume strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Areas for improvement")
    missing_keywords: List[str] = Field(default_factory=list, description="Missing important keywords")
    
    recommendations: List[ResumeRecommendation] = Field(
        default_factory=list,
        description="Specific improvement recommendations"
    )
    
    sections_analysis: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Analysis of individual resume sections"
    )


class CoverLetterResult(BaseModel):
    """Generated cover letter"""
    content: str = Field(..., description="Cover letter content")
    tone: ToneEnum = Field(..., description="Applied tone")
    word_count: int = Field(..., description="Word count")
    
    key_points: List[str] = Field(default_factory=list, description="Key points highlighted")
    company_specific_elements: List[str] = Field(
        default_factory=list,
        description="Company-specific elements included"
    )
    
    customization_score: float = Field(..., ge=0, le=1, description="Customization level score")


class ApplicationStrategyResult(BaseModel):
    """Application strategy recommendations"""
    overall_fit: float = Field(..., ge=0, le=1, description="Overall job fit score")
    application_priority: str = Field(..., description="Application priority (high, medium, low)")
    
    strengths_to_highlight: List[str] = Field(default_factory=list)
    potential_concerns: List[str] = Field(default_factory=list)
    addressing_strategies: List[str] = Field(default_factory=list)
    
    interview_preparation: List[str] = Field(default_factory=list)
    salary_guidance: Optional[Dict[str, Any]] = Field(None)
    
    timeline_recommendations: Dict[str, str] = Field(default_factory=dict)


class AnalysisResults(BaseModel):
    """Complete analysis results"""
    session_id: str = Field(..., description="Session identifier")
    job_analysis: JobAnalysisResult = Field(..., description="Job analysis results")
    company_research: CompanyResearchResult = Field(..., description="Company research results")
    resume_analysis: ResumeAnalysisResult = Field(..., description="Resume analysis results")
    cover_letter: CoverLetterResult = Field(..., description="Generated cover letter")
    application_strategy: ApplicationStrategyResult = Field(..., description="Application strategy")
    
    processing_time: float = Field(..., description="Total processing time in seconds")
    completed_at: datetime = Field(default_factory=datetime.utcnow)


# File Upload Models
class FileInfo(BaseModel):
    """File information model"""
    filename: str = Field(..., description="Original filename")
    file_format: FileFormatEnum = Field(..., description="File format")
    file_size: int = Field(..., ge=1, description="File size in bytes")
    content_type: str = Field(..., description="MIME content type")
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)


class FileUploadResponse(BaseModel):
    """File upload response model"""
    file_id: str = Field(..., description="Unique file identifier")
    file_info: FileInfo = Field(..., description="File information")
    processing_status: ProcessingStatusEnum = Field(..., description="Processing status")
    message: str = Field(..., description="Upload status message")


# Session and History Models
class SessionInfo(BaseModel):
    """Session information model"""
    session_id: str = Field(..., description="Session identifier")
    created_at: datetime = Field(..., description="Session creation time")
    status: ProcessingStatusEnum = Field(..., description="Session status")
    job_title: Optional[str] = Field(None, description="Job title being analyzed")
    company_name: Optional[str] = Field(None, description="Company name")
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")


class ApplicationHistory(BaseModel):
    """Application history model"""
    sessions: List[SessionInfo] = Field(default_factory=list, description="Session list")
    total_applications: int = Field(..., description="Total applications processed")
    success_rate: float = Field(..., ge=0, le=1, description="Success rate")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")


# Configuration Models
class ServiceConfiguration(BaseModel):
    """Service configuration model"""
    environment: EnvironmentEnum = Field(..., description="Environment")
    version: str = Field(..., description="Service version")
    features_enabled: List[str] = Field(default_factory=list, description="Enabled features")
    rate_limits: Dict[str, int] = Field(default_factory=dict, description="Rate limit configuration")
    file_limits: Dict[str, Any] = Field(default_factory=dict, description="File processing limits")


# Utility Models
class ValidationError(BaseModel):
    """Validation error detail"""
    field: str = Field(..., description="Field name with error")
    message: str = Field(..., description="Error message")
    invalid_value: Optional[Any] = Field(None, description="Invalid value provided")


class APIVersion(BaseModel):
    """API version information"""
    version: str = Field(..., description="API version")
    supported_features: List[str] = Field(default_factory=list, description="Supported features")
    deprecation_notices: List[str] = Field(default_factory=list, description="Deprecation notices")
    documentation_url: str = Field(..., description="Documentation URL")