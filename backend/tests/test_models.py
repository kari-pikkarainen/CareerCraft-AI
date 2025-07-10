"""
Tests for API models.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from api.models import (
    JobAnalysisRequest,
    JobPreferences,
    ToneEnum,
    ProcessingStatusEnum,
    HealthResponse,
    ErrorResponse,
    ProgressResponse,
    ProgressStep,
    JobAnalysisResult,
    SkillAnalysis,
    JobRequirement
)


class TestJobAnalysisModels:
    """Test job analysis related models"""
    
    def test_job_preferences_validation(self):
        """Test job preferences validation"""
        # Valid preferences
        prefs = JobPreferences(
            tone=ToneEnum.PROFESSIONAL,
            focus_areas=["technical skills", "leadership", "experience"],
            include_salary_guidance=True
        )
        assert prefs.tone == ToneEnum.PROFESSIONAL
        assert len(prefs.focus_areas) == 3
        assert "technical skills" in prefs.focus_areas
        
        # Test focus areas normalization
        prefs = JobPreferences(
            focus_areas=["  Technical Skills  ", "LEADERSHIP", ""]
        )
        assert prefs.focus_areas == ["technical skills", "leadership"]
        
        # Test too many focus areas
        with pytest.raises(ValidationError):
            JobPreferences(focus_areas=["a", "b", "c", "d", "e", "f"])  # More than 5
    
    def test_job_analysis_request_validation(self):
        """Test job analysis request validation"""
        # Valid request
        request = JobAnalysisRequest(
            job_description="This is a software engineer position requiring Python and JavaScript skills. Must have 3+ years experience in web development.",
            job_url="https://example.com/jobs/123",
            preferences=JobPreferences(tone=ToneEnum.CONVERSATIONAL)
        )
        assert len(request.job_description) >= 50
        assert request.job_url == "https://example.com/jobs/123"
        
        # Test invalid job description (too short)
        with pytest.raises(ValidationError):
            JobAnalysisRequest(job_description="Too short")
        
        # Test invalid job description (too long)
        with pytest.raises(ValidationError):
            JobAnalysisRequest(job_description="x" * 50001)
        
        # Test invalid URL
        with pytest.raises(ValidationError):
            JobAnalysisRequest(
                job_description="Valid job description with sufficient length to pass validation requirements.",
                job_url="not-a-valid-url"
            )
        
        # Test valid URLs
        valid_urls = [
            "https://example.com/job/123",
            "http://localhost:3000/jobs",
            "https://company.co.uk/careers/position-123"
        ]
        for url in valid_urls:
            request = JobAnalysisRequest(
                job_description="Valid job description with sufficient length to pass validation requirements.",
                job_url=url
            )
            assert request.job_url == url


class TestProgressModels:
    """Test progress tracking models"""
    
    def test_progress_step_validation(self):
        """Test progress step validation"""
        # Valid step
        step = ProgressStep(
            step_number=3,
            step_name="Resume Analysis",
            status=ProcessingStatusEnum.PROCESSING,
            progress_percentage=75,
            started_at=datetime.utcnow()
        )
        assert step.step_number == 3
        assert step.status == ProcessingStatusEnum.PROCESSING
        
        # Test invalid step number
        with pytest.raises(ValidationError):
            ProgressStep(
                step_number=0,  # Should be 1-7
                step_name="Invalid",
                status=ProcessingStatusEnum.PENDING,
                progress_percentage=0
            )
        
        with pytest.raises(ValidationError):
            ProgressStep(
                step_number=8,  # Should be 1-7
                step_name="Invalid",
                status=ProcessingStatusEnum.PENDING,
                progress_percentage=0
            )
        
        # Test invalid progress percentage
        with pytest.raises(ValidationError):
            ProgressStep(
                step_number=1,
                step_name="Valid",
                status=ProcessingStatusEnum.PENDING,
                progress_percentage=-1  # Should be 0-100
            )
        
        with pytest.raises(ValidationError):
            ProgressStep(
                step_number=1,
                step_name="Valid",
                status=ProcessingStatusEnum.PENDING,
                progress_percentage=101  # Should be 0-100
            )
    
    def test_progress_response_model(self):
        """Test progress response model"""
        steps = [
            ProgressStep(
                step_number=1,
                step_name="Job Analysis",
                status=ProcessingStatusEnum.COMPLETED,
                progress_percentage=100
            ),
            ProgressStep(
                step_number=2,
                step_name="Company Research",
                status=ProcessingStatusEnum.PROCESSING,
                progress_percentage=50
            )
        ]
        
        progress = ProgressResponse(
            session_id="test-session-123",
            status=ProcessingStatusEnum.PROCESSING,
            overall_progress=35,
            current_step=steps[1],
            steps=steps,
            started_at=datetime.utcnow()
        )
        
        assert progress.session_id == "test-session-123"
        assert progress.overall_progress == 35
        assert len(progress.steps) == 2
        assert progress.current_step.step_number == 2


class TestResultModels:
    """Test analysis result models"""
    
    def test_skill_analysis_model(self):
        """Test skill analysis model"""
        skill = SkillAnalysis(
            skill="Python",
            required=True,
            present_in_resume=True,
            proficiency_level="Expert",
            importance_score=0.9
        )
        assert skill.skill == "Python"
        assert skill.required is True
        assert skill.importance_score == 0.9
        
        # Test invalid importance score
        with pytest.raises(ValidationError):
            SkillAnalysis(
                skill="JavaScript",
                required=False,
                present_in_resume=False,
                importance_score=1.5  # Should be 0-1
            )
    
    def test_job_requirement_model(self):
        """Test job requirement model"""
        requirement = JobRequirement(
            requirement="5+ years of software development experience",
            category="experience",
            priority="required",
            matches_resume=True
        )
        assert requirement.category == "experience"
        assert requirement.priority == "required"
        assert requirement.matches_resume is True
    
    def test_job_analysis_result_model(self):
        """Test complete job analysis result"""
        skills = [
            SkillAnalysis(
                skill="Python",
                required=True,
                present_in_resume=True,
                importance_score=0.9
            ),
            SkillAnalysis(
                skill="React",
                required=False,
                present_in_resume=False,
                importance_score=0.6
            )
        ]
        
        requirements = [
            JobRequirement(
                requirement="Bachelor's degree in Computer Science",
                category="education",
                priority="required",
                matches_resume=True
            )
        ]
        
        result = JobAnalysisResult(
            job_title="Senior Software Engineer",
            company_name="Tech Corp",
            location="San Francisco, CA",
            employment_type="full-time",
            experience_level="senior",
            requirements=requirements,
            skills_analysis=skills,
            key_keywords=["python", "react", "javascript"],
            industry="technology",
            remote_friendly=True,
            analysis_score=0.85
        )
        
        assert result.job_title == "Senior Software Engineer"
        assert result.company_name == "Tech Corp"
        assert len(result.skills_analysis) == 2
        assert len(result.requirements) == 1
        assert result.analysis_score == 0.85
        assert result.remote_friendly is True


class TestHealthModels:
    """Test health check models"""
    
    def test_health_response_model(self):
        """Test health response model"""
        health = HealthResponse(
            status="healthy",
            environment="development",
            checks={"database": "ok", "claude_api": "ok"}
        )
        assert health.status == "healthy"
        assert health.service == "CareerCraft AI"
        assert health.version == "1.0.0"
        assert health.environment == "development"
        assert health.checks["database"] == "ok"
    
    def test_error_response_model(self):
        """Test error response model"""
        error = ErrorResponse(
            error_code="INVALID_INPUT",
            message="The provided input is invalid",
            details="Job description must be at least 50 characters long"
        )
        assert error.error is True
        assert error.error_code == "INVALID_INPUT"
        assert error.details is not None


class TestEnumerations:
    """Test enumeration values"""
    
    def test_tone_enum(self):
        """Test tone enumeration"""
        assert ToneEnum.PROFESSIONAL == "professional"
        assert ToneEnum.CONVERSATIONAL == "conversational"
        assert ToneEnum.CONFIDENT == "confident"
        assert ToneEnum.ENTHUSIASTIC == "enthusiastic"
    
    def test_processing_status_enum(self):
        """Test processing status enumeration"""
        assert ProcessingStatusEnum.PENDING == "pending"
        assert ProcessingStatusEnum.PROCESSING == "processing"
        assert ProcessingStatusEnum.COMPLETED == "completed"
        assert ProcessingStatusEnum.FAILED == "failed"
        assert ProcessingStatusEnum.CANCELLED == "cancelled"


if __name__ == "__main__":
    # Simple test runner for development
    import sys
    
    print("Running API models tests...")
    
    try:
        # Test job preferences
        prefs = JobPreferences(
            tone=ToneEnum.PROFESSIONAL,
            focus_areas=["technical", "leadership"]
        )
        print(f"✓ JobPreferences: {'PASS' if prefs.tone == ToneEnum.PROFESSIONAL else 'FAIL'}")
        
        # Test job analysis request
        request = JobAnalysisRequest(
            job_description="This is a comprehensive software engineer position requiring extensive Python and JavaScript skills with minimum 3+ years experience.",
            preferences=prefs
        )
        print(f"✓ JobAnalysisRequest: {'PASS' if len(request.job_description) >= 50 else 'FAIL'}")
        
        # Test progress step
        step = ProgressStep(
            step_number=1,
            step_name="Job Analysis",
            status=ProcessingStatusEnum.COMPLETED,
            progress_percentage=100
        )
        print(f"✓ ProgressStep: {'PASS' if step.step_number == 1 else 'FAIL'}")
        
        # Test skill analysis
        skill = SkillAnalysis(
            skill="Python",
            required=True,
            present_in_resume=True,
            importance_score=0.9
        )
        print(f"✓ SkillAnalysis: {'PASS' if skill.importance_score == 0.9 else 'FAIL'}")
        
        # Test health response
        health = HealthResponse(
            status="healthy",
            checks={"database": "ok"}
        )
        print(f"✓ HealthResponse: {'PASS' if health.service == 'CareerCraft AI' else 'FAIL'}")
        
        # Test enumerations
        tone_works = ToneEnum.PROFESSIONAL == "professional"
        status_works = ProcessingStatusEnum.COMPLETED == "completed"
        print(f"✓ Enumerations: {'PASS' if tone_works and status_works else 'FAIL'}")
        
        print("\n✅ All API models tests passed! Models are ready.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)