"""
Tests for job analysis orchestration service.
"""

import pytest
import asyncio
import json
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone, timedelta

# Mock dependencies before importing
with patch('services.job_analysis_service.get_file_service'), \
     patch('services.job_analysis_service.get_claude_service'), \
     patch('services.job_analysis_service.get_resume_parser'):
    
    from services.job_analysis_service import (
        JobAnalysisService,
        AnalysisStep,
        AnalysisStatus,
        AnalysisRequest,
        AnalysisProgress,
        JobAnalysisError,
        get_job_analysis_service
    )
    from services.auth_service import SessionData


class TestJobAnalysisService:
    """Test job analysis orchestration service"""
    
    def setup_method(self):
        """Setup test environment with mocked services"""
        # Mock dependencies
        self.mock_file_service = MagicMock()
        self.mock_claude_service = AsyncMock()
        self.mock_resume_parser = MagicMock()
        
        # Configure mock Claude service responses
        mock_claude_response = MagicMock()
        mock_claude_response.response_text = '{"job_title": "Software Engineer", "requirements": ["Python", "React"]}'
        mock_claude_response.usage_tokens = 150
        mock_claude_response.processing_time = 2.5
        
        self.mock_claude_service.analyze_job_description = AsyncMock(return_value=mock_claude_response)
        self.mock_claude_service.research_company = AsyncMock(return_value=mock_claude_response)
        self.mock_claude_service.analyze_resume = AsyncMock(return_value=mock_claude_response)
        self.mock_claude_service.generate_cover_letter = AsyncMock(return_value=mock_claude_response)
        self.mock_claude_service.analyze_skills_gap = AsyncMock(return_value=mock_claude_response)
        
        # Mock resume parser
        mock_parsed_resume = MagicMock()
        mock_parsed_resume.contact_info.email = "john@example.com"
        mock_parsed_resume.contact_info.phone = "(555) 123-4567"
        mock_parsed_resume.contact_info.linkedin = None
        mock_parsed_resume.contact_info.github = None
        mock_parsed_resume.contact_info.website = None
        mock_parsed_resume.contact_info.address = None
        mock_parsed_resume.summary = "Experienced software engineer"
        mock_parsed_resume.work_experience = []
        mock_parsed_resume.education = []
        mock_parsed_resume.skills = ["Python", "JavaScript", "React"]
        mock_parsed_resume.projects = []
        mock_parsed_resume.certifications = []
        mock_parsed_resume.languages = []
        mock_parsed_resume.sections = {"summary": "Summary section", "experience": "Experience section"}
        mock_parsed_resume.metadata = {"word_count": 250}
        
        self.mock_resume_parser.parse_resume.return_value = mock_parsed_resume
        
        # Create service instance with mocked dependencies
        with patch('services.job_analysis_service.get_file_service', return_value=self.mock_file_service), \
             patch('services.job_analysis_service.get_claude_service', return_value=self.mock_claude_service), \
             patch('services.job_analysis_service.get_resume_parser', return_value=self.mock_resume_parser):
            
            self.service = JobAnalysisService()
    
    def test_service_initialization(self):
        """Test service initialization"""
        assert self.service is not None
        assert hasattr(self.service, 'active_jobs')
        assert hasattr(self.service, 'job_progress')
        assert hasattr(self.service, 'job_results')
        assert len(self.service.STEP_CONFIG) == 7
    
    def test_step_configuration(self):
        """Test step configuration completeness"""
        expected_steps = [
            AnalysisStep.JOB_ANALYSIS,
            AnalysisStep.COMPANY_RESEARCH,
            AnalysisStep.RESUME_PARSING,
            AnalysisStep.SKILLS_ANALYSIS,
            AnalysisStep.RESUME_ENHANCEMENT,
            AnalysisStep.COVER_LETTER,
            AnalysisStep.FINAL_REVIEW
        ]
        
        for step in expected_steps:
            assert step in self.service.STEP_CONFIG
            config = self.service.STEP_CONFIG[step]
            assert "step_number" in config
            assert "step_name" in config
            assert "progress_percentage" in config
            assert "description" in config
        
        # Check progress percentages are in ascending order
        percentages = [config["progress_percentage"] for config in self.service.STEP_CONFIG.values()]
        assert percentages == sorted(percentages)
        assert percentages[-1] == 100  # Final step should be 100%
    
    @pytest.mark.asyncio
    async def test_start_analysis_with_resume_text(self):
        """Test starting analysis with resume text"""
        session_data = SessionData(
            session_id="test_session",
            user_id="test_user",
            api_key="test_key",
            permissions=["read", "write"],
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc)
        )
        
        job_description = "Software Engineer position requiring Python and React experience for building web applications."
        resume_text = "John Doe, Software Engineer with 5 years Python experience. Built web applications using Django and React."
        
        analysis_id = await self.service.start_analysis(
            session_data=session_data,
            job_description=job_description,
            resume_text=resume_text,
            preferences={"tone": "professional", "focus_areas": ["technical skills"]}
        )
        
        assert analysis_id.startswith("analysis_")
        assert analysis_id in self.service.active_jobs
        assert analysis_id in self.service.job_progress
        
        # Check job initialization
        job = self.service.active_jobs[analysis_id]
        assert job["request"].session_id == session_data.session_id
        assert job["request"].job_description == job_description
        assert job["request"].resume_text == resume_text
        assert job["status"] == AnalysisStatus.PENDING
        
        # Check progress initialization
        progress_list = self.service.job_progress[analysis_id]
        assert len(progress_list) == 7
        
        for progress in progress_list:
            assert progress.status == AnalysisStatus.PENDING
            assert progress.step_number >= 1 and progress.step_number <= 7
    
    @pytest.mark.asyncio
    async def test_start_analysis_validation(self):
        """Test input validation for start_analysis"""
        session_data = SessionData(
            session_id="test_session",
            user_id="test_user",
            api_key="test_key",
            permissions=[],
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc)
        )
        
        # Test short job description
        with pytest.raises(JobAnalysisError, match="at least 50 characters"):
            await self.service.start_analysis(
                session_data=session_data,
                job_description="Short job",
                resume_text="Some resume text"
            )
        
        # Test missing resume data
        with pytest.raises(JobAnalysisError, match="Either resume file or resume text"):
            await self.service.start_analysis(
                session_data=session_data,
                job_description="Software Engineer position requiring Python and React experience for building web applications."
            )
    
    def test_progress_tracking(self):
        """Test progress tracking functionality"""
        # Create a mock analysis job
        analysis_id = "test_analysis_123"
        self.service.active_jobs[analysis_id] = {
            "status": AnalysisStatus.PROCESSING,
            "started_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Initialize progress
        self.service.job_progress[analysis_id] = []
        for step in AnalysisStep:
            config = self.service.STEP_CONFIG[step]
            progress = AnalysisProgress(
                step=step,
                step_number=config["step_number"],
                step_name=config["step_name"],
                status=AnalysisStatus.PENDING,
                progress_percentage=config["progress_percentage"]
            )
            self.service.job_progress[analysis_id].append(progress)
        
        # Test getting progress
        progress_data = self.service.get_progress(analysis_id)
        
        assert progress_data is not None
        assert progress_data["analysis_id"] == analysis_id
        assert progress_data["overall_progress"] == 0  # No steps completed yet
        assert len(progress_data["steps"]) == 7
        
        # Simulate completing first step
        asyncio.run(self.service._update_step_status(
            analysis_id, 
            AnalysisStep.JOB_ANALYSIS, 
            AnalysisStatus.COMPLETED
        ))
        
        updated_progress = self.service.get_progress(analysis_id)
        assert updated_progress["overall_progress"] > 0
    
    def test_job_match_score_calculation(self):
        """Test job match score calculation"""
        job_analysis = {
            "keywords": ["Python", "React", "JavaScript", "Django"]
        }
        
        parsed_resume = {
            "skills": ["Python", "React", "HTML", "CSS"],
            "work_experience": [{"company": "TechCorp"}, {"company": "StartupCo"}],
            "education": [{"degree": "BS Computer Science"}],
            "contact_info": {"email": "john@example.com", "phone": "(555) 123-4567"}
        }
        
        skills_analysis = {}
        
        score = self.service._calculate_job_match_score(job_analysis, parsed_resume, skills_analysis)
        
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be a reasonable match
    
    def test_application_strength_assessment(self):
        """Test application strength assessment"""
        job_analysis = {"keywords": ["Python", "React"]}
        parsed_resume = {"skills": ["Python", "React", "JavaScript"], "work_experience": [{}], "education": [{}], "contact_info": {"email": "test@example.com"}}
        skills_analysis = {}
        
        strength = self.service._assess_application_strength(job_analysis, parsed_resume, skills_analysis)
        assert isinstance(strength, str)
        assert any(keyword in strength.lower() for keyword in ["strong", "good", "moderate", "developing"])
    
    def test_cancel_analysis(self):
        """Test analysis cancellation"""
        analysis_id = "test_analysis_cancel"
        
        # Create active job
        self.service.active_jobs[analysis_id] = {
            "status": AnalysisStatus.PROCESSING,
            "started_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Initialize progress with one processing step
        self.service.job_progress[analysis_id] = [
            AnalysisProgress(
                step=AnalysisStep.JOB_ANALYSIS,
                step_number=1,
                step_name="Job Analysis",
                status=AnalysisStatus.PROCESSING,
                progress_percentage=14
            )
        ]
        
        # Test cancellation
        result = self.service.cancel_analysis(analysis_id)
        assert result is True
        
        # Check status updated
        job = self.service.active_jobs[analysis_id]
        assert job["status"] == AnalysisStatus.CANCELLED
        
        # Check step status updated
        progress = self.service.job_progress[analysis_id][0]
        assert progress.status == AnalysisStatus.CANCELLED
        
        # Test cancelling non-existent job
        result = self.service.cancel_analysis("non_existent")
        assert result is False
        
        # Test cancelling already completed job
        job["status"] = AnalysisStatus.COMPLETED
        result = self.service.cancel_analysis(analysis_id)
        assert result is False
    
    def test_cleanup_old_jobs(self):
        """Test cleanup of old jobs"""
        # Create old job
        old_time = datetime.now(timezone.utc) - timedelta(hours=25)
        analysis_id = "old_job"
        
        self.service.active_jobs[analysis_id] = {
            "status": AnalysisStatus.COMPLETED,
            "started_at": old_time,
            "updated_at": old_time
        }
        self.service.job_progress[analysis_id] = []
        self.service.job_results[analysis_id] = MagicMock()
        
        # Create recent job
        recent_time = datetime.now(timezone.utc) - timedelta(hours=1)
        recent_id = "recent_job"
        
        self.service.active_jobs[recent_id] = {
            "status": AnalysisStatus.PROCESSING,
            "started_at": recent_time,
            "updated_at": recent_time
        }
        
        # Test cleanup
        cleaned_count = self.service.cleanup_old_jobs(max_age_hours=24)
        
        assert cleaned_count == 1
        assert analysis_id not in self.service.active_jobs
        assert recent_id in self.service.active_jobs
    
    def test_singleton_pattern(self):
        """Test job analysis service singleton pattern"""
        service1 = get_job_analysis_service()
        service2 = get_job_analysis_service()
        assert service1 is service2


class TestAnalysisWorkflow:
    """Test complete analysis workflow execution"""
    
    def setup_method(self):
        """Setup test environment"""
        self.mock_claude_service = AsyncMock()
        self.mock_resume_parser = MagicMock()
        
        # Configure successful Claude responses
        def create_claude_response(text):
            response = MagicMock()
            response.response_text = text
            response.usage_tokens = 150
            response.processing_time = 2.0
            return response
        
        self.mock_claude_service.analyze_job_description.return_value = create_claude_response(
            '{"job_title": "Senior Software Engineer", "company_name": "TechCorp", "requirements": ["Python", "React", "5+ years experience"]}'
        )
        
        self.mock_claude_service.research_company.return_value = create_claude_response(
            '{"company_name": "TechCorp", "industry": "Technology", "culture_insights": ["Innovation-focused", "Remote-friendly"]}'
        )
        
        self.mock_claude_service.analyze_skills_gap.return_value = create_claude_response(
            '{"missing_skills": ["React", "AWS"], "recommendations": ["Learn React fundamentals", "Get AWS certification"]}'
        )
        
        self.mock_claude_service.analyze_resume.return_value = create_claude_response(
            '{"overall_score": 8.5, "recommendations": ["Add more quantified achievements", "Include React projects"]}'
        )
        
        self.mock_claude_service.generate_cover_letter.return_value = create_claude_response(
            "Dear Hiring Manager,\n\nI am excited to apply for the Senior Software Engineer position at TechCorp..."
        )
        
        # Configure resume parser
        mock_parsed_resume = MagicMock()
        mock_parsed_resume.contact_info.email = "john@example.com"
        mock_parsed_resume.contact_info.phone = "(555) 123-4567"
        mock_parsed_resume.contact_info.linkedin = "linkedin.com/in/johndoe"
        mock_parsed_resume.contact_info.github = "github.com/johndoe"
        mock_parsed_resume.contact_info.website = None
        mock_parsed_resume.contact_info.address = None
        mock_parsed_resume.summary = "Experienced software engineer with 5 years of Python development"
        mock_parsed_resume.work_experience = [MagicMock(), MagicMock()]  # 2 positions
        mock_parsed_resume.education = [MagicMock()]  # 1 degree
        mock_parsed_resume.skills = ["Python", "JavaScript", "Django", "PostgreSQL"]
        mock_parsed_resume.projects = [MagicMock()]
        mock_parsed_resume.certifications = []
        mock_parsed_resume.languages = ["English"]
        mock_parsed_resume.sections = {"summary": "Summary content", "experience": "Experience content"}
        mock_parsed_resume.metadata = {"word_count": 350}
        
        self.mock_resume_parser.parse_resume.return_value = mock_parsed_resume
    
    @pytest.mark.asyncio
    async def test_complete_workflow_execution(self):
        """Test execution of complete 7-step workflow"""
        # Create service with mocked dependencies
        with patch('services.job_analysis_service.get_file_service'), \
             patch('services.job_analysis_service.get_claude_service', return_value=self.mock_claude_service), \
             patch('services.job_analysis_service.get_resume_parser', return_value=self.mock_resume_parser):
            
            service = JobAnalysisService()
            
            # Create test request
            request = AnalysisRequest(
                session_id="test_session",
                user_id="test_user",
                job_description="Senior Software Engineer position at TechCorp requiring Python, React, and 5+ years experience in web development.",
                resume_text="John Doe, Software Engineer with 5 years Python experience. Built web applications using Django and PostgreSQL."
            )
            
            analysis_id = "test_workflow"
            service.active_jobs[analysis_id] = {
                "request": request,
                "status": AnalysisStatus.PROCESSING,
                "started_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            # Initialize progress tracking
            service.job_progress[analysis_id] = []
            for step in AnalysisStep:
                config = service.STEP_CONFIG[step]
                progress = AnalysisProgress(
                    step=step,
                    step_number=config["step_number"],
                    step_name=config["step_name"],
                    status=AnalysisStatus.PENDING,
                    progress_percentage=config["progress_percentage"]
                )
                service.job_progress[analysis_id].append(progress)
            
            # Execute individual steps
            job_analysis = await service._execute_step_1_job_analysis(analysis_id, request)
            assert "job_title" in job_analysis
            assert job_analysis["job_title"] == "Senior Software Engineer"
            
            company_research = await service._execute_step_2_company_research(analysis_id, request, job_analysis)
            assert "company_name" in company_research
            assert company_research["company_name"] == "TechCorp"
            
            parsed_resume = await service._execute_step_3_resume_parsing(analysis_id, request)
            assert "contact_info" in parsed_resume
            assert parsed_resume["contact_info"]["email"] == "john@example.com"
            
            skills_analysis = await service._execute_step_4_skills_analysis(analysis_id, request, job_analysis, parsed_resume)
            assert "missing_skills" in skills_analysis
            
            resume_enhancement = await service._execute_step_5_resume_enhancement(analysis_id, request, job_analysis, parsed_resume, skills_analysis)
            assert "overall_score" in resume_enhancement
            
            cover_letter = await service._execute_step_6_cover_letter(analysis_id, request, job_analysis, company_research, parsed_resume)
            assert "content" in cover_letter
            assert "Dear Hiring Manager" in cover_letter["content"]
            
            final_summary = await service._execute_step_7_final_review(analysis_id, request, job_analysis, company_research, parsed_resume, skills_analysis, resume_enhancement, cover_letter)
            assert "job_match_score" in final_summary
            assert "key_findings" in final_summary
            
            # Verify all Claude API calls were made
            assert self.mock_claude_service.analyze_job_description.called
            assert self.mock_claude_service.research_company.called
            assert self.mock_claude_service.analyze_skills_gap.called
            assert self.mock_claude_service.analyze_resume.called
            assert self.mock_claude_service.generate_cover_letter.called


if __name__ == "__main__":
    # Simple test runner for development
    import sys
    
    print("Running job analysis service tests...")
    
    try:
        # Mock dependencies for standalone test
        with patch('services.job_analysis_service.get_file_service'), \
             patch('services.job_analysis_service.get_claude_service'), \
             patch('services.job_analysis_service.get_resume_parser'):
            
            # Test service initialization
            service = JobAnalysisService()
            print("✓ JobAnalysisService initialization: PASS")
            
            # Test step configuration
            assert len(service.STEP_CONFIG) == 7
            for step in AnalysisStep:
                assert step in service.STEP_CONFIG
            print("✓ Step configuration: PASS")
            
            # Test progress tracking
            analysis_id = "test_123"
            service.active_jobs[analysis_id] = {
                "status": AnalysisStatus.PROCESSING,
                "started_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            service.job_progress[analysis_id] = []
            
            progress_data = service.get_progress(analysis_id)
            assert progress_data["analysis_id"] == analysis_id
            print("✓ Progress tracking: PASS")
            
            # Test job match calculation
            job_analysis = {"keywords": ["Python", "React"]}
            parsed_resume = {"skills": ["Python"], "work_experience": [{}], "education": [{}], "contact_info": {"email": "test@example.com"}}
            skills_analysis = {}
            
            score = service._calculate_job_match_score(job_analysis, parsed_resume, skills_analysis)
            assert 0.0 <= score <= 1.0
            print("✓ Job match score calculation: PASS")
            
            # Test cancellation
            result = service.cancel_analysis(analysis_id)
            assert result is True
            print("✓ Analysis cancellation: PASS")
            
            # Test singleton
            service1 = get_job_analysis_service()
            service2 = get_job_analysis_service()
            assert service1 is service2
            print("✓ Singleton pattern: PASS")
        
        print("\n✅ All job analysis service tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)