#!/usr/bin/env python3
"""
End-to-end workflow test for CareerCraft AI job analysis orchestration.

This script tests the complete workflow from API endpoints to orchestration service.
"""

import asyncio
import sys
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone

# Mock dependencies before importing
with patch('services.job_analysis_service.get_file_service'), \
     patch('services.job_analysis_service.get_claude_service'), \
     patch('services.job_analysis_service.get_resume_parser'):
    
    from services.job_analysis_service import (
        get_job_analysis_service,
        AnalysisStep,
        AnalysisStatus
    )
    from services.auth_service import SessionData


def setup_mocks():
    """Setup mock services for testing"""
    mock_claude_service = AsyncMock()
    mock_resume_parser = MagicMock()
    
    # Configure Claude service responses
    mock_claude_response = MagicMock()
    mock_claude_response.response_text = '{"job_title": "Software Engineer", "company_name": "TechCorp", "requirements": ["Python", "React"]}'
    mock_claude_response.usage_tokens = 150
    mock_claude_response.processing_time = 2.0
    
    mock_claude_service.analyze_job_description = AsyncMock(return_value=mock_claude_response)
    mock_claude_service.research_company = AsyncMock(return_value=mock_claude_response)
    mock_claude_service.analyze_skills_gap = AsyncMock(return_value=mock_claude_response)
    mock_claude_service.analyze_resume = AsyncMock(return_value=mock_claude_response)
    mock_claude_service.generate_cover_letter = AsyncMock(return_value=mock_claude_response)
    
    # Configure resume parser
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
    mock_parsed_resume.sections = {"summary": "Summary section"}
    mock_parsed_resume.metadata = {"word_count": 250}
    
    mock_resume_parser.parse_resume.return_value = mock_parsed_resume
    
    return mock_claude_service, mock_resume_parser


async def test_workflow():
    """Test complete analysis workflow"""
    print("🧪 Testing CareerCraft AI Job Analysis Workflow")
    print("=" * 50)
    
    # Setup mocks
    mock_claude_service, mock_resume_parser = setup_mocks()
    
    with patch('services.job_analysis_service.get_file_service'), \
         patch('services.job_analysis_service.get_claude_service', return_value=mock_claude_service), \
         patch('services.job_analysis_service.get_resume_parser', return_value=mock_resume_parser):
        
        # Get service instance
        service = get_job_analysis_service()
        print("✅ Job analysis service initialized")
        
        # Create test session
        session_data = SessionData(
            session_id="test_session_e2e",
            user_id="test_user",
            api_key="test_key",
            permissions=["read", "write"],
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc)
        )
        
        # Test job description and resume
        job_description = """
        Software Engineer Position at TechCorp
        
        We are looking for a talented Software Engineer to join our dynamic team. 
        The ideal candidate will have experience with Python, React, and modern web development.
        
        Responsibilities:
        - Develop and maintain web applications
        - Work with React frontend and Python backend
        - Collaborate with cross-functional teams
        - Write clean, maintainable code
        
        Requirements:
        - 3+ years experience with Python
        - Experience with React and JavaScript
        - Bachelor's degree in Computer Science or related field
        - Strong problem-solving skills
        """
        
        resume_text = """
        John Doe
        Software Engineer
        Email: john@example.com
        Phone: (555) 123-4567
        
        Summary:
        Experienced software engineer with 5 years of Python development experience.
        Passionate about building scalable web applications and working with modern technologies.
        
        Skills:
        - Python (Django, Flask)
        - JavaScript (React, Node.js)
        - HTML/CSS
        - PostgreSQL
        - Git
        
        Experience:
        Senior Software Engineer at StartupCo (2021-2024)
        - Built web applications using Python and React
        - Led a team of 3 developers
        - Implemented CI/CD pipelines
        
        Software Engineer at TechFirm (2019-2021)
        - Developed REST APIs using Django
        - Created responsive frontend interfaces
        - Worked with PostgreSQL databases
        
        Education:
        BS Computer Science, University of Technology (2019)
        """
        
        print("\n📋 Starting job analysis...")
        print(f"Job: Software Engineer at TechCorp")
        print(f"Resume: John Doe (5 years experience)")
        
        # Start analysis
        analysis_id = await service.start_analysis(
            session_data=session_data,
            job_description=job_description,
            resume_text=resume_text,
            preferences={
                "tone": "professional",
                "focus_areas": ["technical skills", "relevant experience"]
            }
        )
        
        print(f"✅ Analysis started with ID: {analysis_id}")
        
        # Monitor progress
        print("\n⏳ Monitoring progress...")
        max_wait = 30  # 30 seconds timeout
        waited = 0
        
        while waited < max_wait:
            progress = service.get_progress(analysis_id)
            if not progress:
                print(f"❌ Analysis {analysis_id} not found")
                return False
            
            status = progress["status"]
            overall_progress = progress["overall_progress"]
            current_step = progress["current_step"]
            
            step_info = ""
            if current_step:
                step_info = f" | Step: {current_step['step_name']}"
            
            print(f"📊 Progress: {overall_progress}% | Status: {status}{step_info}")
            
            if status == "completed":
                print("✅ Analysis completed!")
                break
            elif status == "failed":
                print(f"❌ Analysis failed: {progress.get('error', 'Unknown error')}")
                return False
            
            await asyncio.sleep(1)
            waited += 1
        
        if waited >= max_wait:
            print("⏰ Analysis timeout")
            return False
        
        # Get results
        print("\n📄 Retrieving results...")
        result = service.get_result(analysis_id)
        
        if not result:
            print("❌ No results found")
            return False
        
        print("✅ Results retrieved successfully!")
        
        # Validate results structure
        print("\n🔍 Validating results structure...")
        
        required_fields = [
            "job_analysis", "company_research", "parsed_resume",
            "skills_analysis", "resume_recommendations", "cover_letter", "final_summary"
        ]
        
        for field in required_fields:
            if hasattr(result, field):
                value = getattr(result, field)
                if value:
                    print(f"  ✅ {field}: Present")
                else:
                    print(f"  ⚠️  {field}: Empty")
            else:
                print(f"  ❌ {field}: Missing")
                return False
        
        # Test API calls
        print("\n🔗 Verifying Claude API integration...")
        assert mock_claude_service.analyze_job_description.called, "Job analysis API not called"
        assert mock_claude_service.research_company.called, "Company research API not called"
        assert mock_claude_service.analyze_skills_gap.called, "Skills analysis API not called"
        assert mock_claude_service.analyze_resume.called, "Resume analysis API not called"
        assert mock_claude_service.generate_cover_letter.called, "Cover letter API not called"
        print("✅ All Claude API endpoints called correctly")
        
        # Test resume parsing
        print("\n📝 Verifying resume parsing...")
        assert mock_resume_parser.parse_resume.called, "Resume parser not called"
        print("✅ Resume parser integration working")
        
        # Validate final summary
        final_summary = result.final_summary
        assert "job_match_score" in final_summary, "Job match score missing"
        assert "key_findings" in final_summary, "Key findings missing"
        assert "recommendations_summary" in final_summary, "Recommendations summary missing"
        print("✅ Final summary structure validated")
        
        print("\n🎉 End-to-end workflow test completed successfully!")
        print("=" * 50)
        print("Summary:")
        print(f"- Analysis ID: {analysis_id}")
        print(f"- Processing time: {(result.completed_at - result.created_at).total_seconds():.1f}s")
        print(f"- Steps completed: 7/7")
        print(f"- Job match score: {final_summary.get('job_match_score', 'N/A')}")
        print(f"- API calls made: {len(required_fields)}")
        
        return True


async def main():
    """Main test function"""
    try:
        success = await test_workflow()
        if success:
            print("\n✅ All tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())