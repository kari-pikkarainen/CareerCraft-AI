"""
Tests for user ownership validation in analysis API endpoints.

Tests security features to prevent cross-user data access.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from fastapi import HTTPException

from services.auth_service import SessionData
from services.job_analysis_service import (
    JobAnalysisService,
    AnalysisRequest,
    AnalysisStatus,
    AnalysisStep
)


class TestAnalysisAPISecurityValidation:
    """Test user ownership validation in analysis API endpoints"""
    
    def setup_method(self):
        """Setup test environment"""
        # Create mock job analysis service
        self.mock_job_analysis_service = MagicMock()
        
        # Mock active jobs with different user IDs
        self.user1_analysis_id = "analysis_user1_test"
        self.user2_analysis_id = "analysis_user2_test"
        
        # Create mock requests for different users
        self.user1_request = AnalysisRequest(
            session_id="session1",
            user_id="user1",
            job_description="Software Engineer position",
            resume_text="John Doe resume content"
        )
        
        self.user2_request = AnalysisRequest(
            session_id="session2", 
            user_id="user2",
            job_description="Data Scientist position",
            resume_text="Jane Smith resume content"
        )
        
        # Mock active jobs data
        self.mock_job_analysis_service.active_jobs = {
            self.user1_analysis_id: {
                "request": self.user1_request,
                "status": AnalysisStatus.COMPLETED,
                "current_step": AnalysisStep.FINAL_REVIEW,
                "started_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            },
            self.user2_analysis_id: {
                "request": self.user2_request,
                "status": AnalysisStatus.PROCESSING,
                "current_step": AnalysisStep.SKILLS_ANALYSIS,
                "started_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        }
        
        # Mock progress data
        self.mock_job_analysis_service.get_progress.return_value = {
            "status": "processing",
            "overall_progress": 57,
            "current_step": "skills_analysis",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Mock results data
        self.mock_result = MagicMock()
        self.mock_result.session_id = "session1"
        self.mock_result.completed_at = datetime.now(timezone.utc)
        self.mock_result.processing_metadata = {"total_processing_time": 35.2}
        self.mock_result.job_analysis = {"job_title": "Software Engineer"}
        self.mock_result.company_research = {"company": "TechCorp"}
        self.mock_result.parsed_resume = {"name": "John Doe"}
        self.mock_result.skills_analysis = {"match_score": 85}
        self.mock_result.resume_recommendations = {"improvements": ["Add more keywords"]}
        self.mock_result.cover_letter = {"content": "Dear Hiring Manager..."}
        self.mock_result.final_summary = {"score": 88}
        
        self.mock_job_analysis_service.get_result.return_value = self.mock_result
        self.mock_job_analysis_service.cancel_analysis.return_value = True
        
        # Create session data for different users
        self.user1_session = SessionData(
            session_id="session1",
            user_id="user1",
            permissions=["analyze"]
        )
        
        self.user2_session = SessionData(
            session_id="session2", 
            user_id="user2",
            permissions=["analyze"]
        )
        
        # Mock the service getter
        self.get_job_analysis_service_patcher = patch(
            'api.analysis.get_job_analysis_service',
            return_value=self.mock_job_analysis_service
        )
        self.get_job_analysis_service_patcher.start()
    
    def teardown_method(self):
        """Clean up after each test"""
        self.get_job_analysis_service_patcher.stop()
    
    def test_progress_endpoint_user_ownership_validation(self):
        """Test that progress endpoint validates user ownership"""
        # Import here to avoid circular imports
        from api.analysis import get_analysis_progress
        
        # Test 1: User can access their own analysis
        self.mock_job_analysis_service.get_progress.return_value = {
            "status": "processing",
            "overall_progress": 57
        }
        
        # This should succeed
        result = asyncio.run(get_analysis_progress(self.user1_analysis_id, self.user1_session))
        assert result["status"] == "processing"
        assert result["overall_progress"] == 57
        
        # Test 2: User cannot access another user's analysis
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_analysis_progress(self.user1_analysis_id, self.user2_session))
        
        assert exc_info.value.status_code == 403
        assert "permission" in str(exc_info.value.detail).lower()
        
        # Test 3: Non-existent analysis returns 404
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_analysis_progress("non_existent_analysis", self.user1_session))
        
        assert exc_info.value.status_code == 404
    
    def test_results_endpoint_user_ownership_validation(self):
        """Test that results endpoint validates user ownership"""
        from api.analysis import get_analysis_results
        
        # Test 1: User can access their own completed analysis results
        # Mock completed progress
        self.mock_job_analysis_service.get_progress.return_value = {
            "status": "completed",
            "overall_progress": 100
        }
        
        result = asyncio.run(get_analysis_results(self.user1_analysis_id, self.user1_session))
        assert result["analysis_id"] == self.user1_analysis_id
        assert result["session_id"] == "session1"
        assert "job_analysis" in result
        assert "company_research" in result
        assert "parsed_resume" in result
        
        # Test 2: User cannot access another user's analysis results
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_analysis_results(self.user1_analysis_id, self.user2_session))
        
        assert exc_info.value.status_code == 403
        assert "permission" in str(exc_info.value.detail).lower()
        
        # Test 3: Accessing incomplete analysis returns 400
        # Mock incomplete progress
        self.mock_job_analysis_service.get_progress.return_value = {
            "status": "processing",
            "overall_progress": 57
        }
        
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_analysis_results(self.user2_analysis_id, self.user2_session))
        
        assert exc_info.value.status_code == 400
        assert "not yet completed" in str(exc_info.value.detail)
    
    def test_cancel_endpoint_user_ownership_validation(self):
        """Test that cancel endpoint validates user ownership"""
        from api.analysis import cancel_analysis
        
        # Test 1: User can cancel their own analysis
        result = asyncio.run(cancel_analysis(self.user1_analysis_id, self.user1_session))
        assert result["status"] == "cancelled"
        assert self.user1_analysis_id in result["message"]
        
        # Test 2: User cannot cancel another user's analysis
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(cancel_analysis(self.user1_analysis_id, self.user2_session))
        
        assert exc_info.value.status_code == 403
        assert "permission" in str(exc_info.value.detail).lower()
        
        # Test 3: Non-existent analysis returns 404
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(cancel_analysis("non_existent_analysis", self.user1_session))
        
        assert exc_info.value.status_code == 404
    
    def test_history_endpoint_user_filtering(self):
        """Test that history endpoint only returns user's own analyses"""
        from api.analysis import get_analysis_history
        
        # Test 1: User 1 should only see their own analyses
        result = asyncio.run(get_analysis_history(limit=10, offset=0, session=self.user1_session))
        
        # Should only return user1's analyses
        assert "analyses" in result
        assert len(result["analyses"]) == 1
        assert result["analyses"][0]["analysis_id"] == self.user1_analysis_id
        assert result["total"] == 1
        
        # Test 2: User 2 should only see their own analyses
        result = asyncio.run(get_analysis_history(limit=10, offset=0, session=self.user2_session))
        
        # Should only return user2's analyses
        assert "analyses" in result
        assert len(result["analyses"]) == 1
        assert result["analyses"][0]["analysis_id"] == self.user2_analysis_id
        assert result["total"] == 1
        
        # Test 3: Pagination works correctly with user filtering
        result = asyncio.run(get_analysis_history(limit=1, offset=0, session=self.user1_session))
        
        assert len(result["analyses"]) == 1
        assert result["limit"] == 1
        assert result["offset"] == 0
        assert result["has_more"] == False
    
    def test_cross_user_data_isolation(self):
        """Test comprehensive data isolation between users"""
        # This is an integration test that verifies complete isolation
        
        # User 1 operations
        user1_operations = [
            ("progress", self.user1_analysis_id),
            ("results", self.user1_analysis_id),
            ("cancel", self.user1_analysis_id)
        ]
        
        # User 2 operations
        user2_operations = [
            ("progress", self.user2_analysis_id),
            ("results", self.user2_analysis_id),
            ("cancel", self.user2_analysis_id)
        ]
        
        # Test that each user can only access their own data
        for operation, analysis_id in user1_operations:
            # User 1 should be able to access their own analysis
            try:
                if operation == "progress":
                    from api.analysis import get_analysis_progress
                    self.mock_job_analysis_service.get_progress.return_value = {"status": "processing"}
                    asyncio.run(get_analysis_progress(analysis_id, self.user1_session))
                elif operation == "results":
                    from api.analysis import get_analysis_results
                    self.mock_job_analysis_service.get_progress.return_value = {"status": "completed"}
                    asyncio.run(get_analysis_results(analysis_id, self.user1_session))
                elif operation == "cancel":
                    from api.analysis import cancel_analysis
                    asyncio.run(cancel_analysis(analysis_id, self.user1_session))
            except HTTPException as e:
                # Only accept 400 errors for business logic (like incomplete analysis)
                if e.status_code != 400:
                    pytest.fail(f"User should be able to access their own {operation}: {e.detail}")
        
        # Test that each user cannot access other user's data
        for operation, analysis_id in user1_operations:
            # User 2 should NOT be able to access user 1's analysis
            with pytest.raises(HTTPException) as exc_info:
                if operation == "progress":
                    from api.analysis import get_analysis_progress
                    asyncio.run(get_analysis_progress(analysis_id, self.user2_session))
                elif operation == "results":
                    from api.analysis import get_analysis_results
                    asyncio.run(get_analysis_results(analysis_id, self.user2_session))
                elif operation == "cancel":
                    from api.analysis import cancel_analysis
                    asyncio.run(cancel_analysis(analysis_id, self.user2_session))
            
            assert exc_info.value.status_code == 403
            assert "permission" in str(exc_info.value.detail).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])