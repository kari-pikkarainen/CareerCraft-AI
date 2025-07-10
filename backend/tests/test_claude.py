"""
Tests for Claude API integration service.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

# Mock configuration before importing Claude service
with patch('services.claude_service.get_config') as mock_config:
    mock_claude = MagicMock()
    mock_claude.api_key = "test-api-key"
    mock_claude.base_url = "https://api.anthropic.com"
    mock_claude.timeout = 30
    mock_config.return_value.claude = mock_claude
    
    from services.claude_service import (
        ClaudeService,
        ClaudeAPIError,
        PromptType,
        AnalysisResult,
        get_claude_service
    )


class TestClaudeService:
    """Test Claude API service functionality"""
    
    @patch('services.claude_service.Anthropic')
    @patch('services.claude_service.AsyncAnthropic')
    def setup_method(self, mock_async_anthropic, mock_anthropic):
        """Setup test environment with mocked Claude clients"""
        # Mock the clients
        self.mock_sync_client = MagicMock()
        self.mock_async_client = AsyncMock()
        
        mock_anthropic.return_value = self.mock_sync_client
        mock_async_anthropic.return_value = self.mock_async_client
        
        # Create service instance
        with patch('services.claude_service.get_config') as mock_config:
            mock_claude_config = MagicMock()
            mock_claude_config.api_key = "test-api-key"
            mock_config.return_value.claude = mock_claude_config
            
            self.claude_service = ClaudeService()
    
    def test_service_initialization(self):
        """Test Claude service initialization"""
        assert self.claude_service is not None
        assert hasattr(self.claude_service, 'sync_client')
        assert hasattr(self.claude_service, 'async_client')
        assert hasattr(self.claude_service, 'prompts')
        
        # Check prompt templates are loaded
        assert PromptType.JOB_ANALYSIS in self.claude_service.prompts
        assert PromptType.COMPANY_RESEARCH in self.claude_service.prompts
        assert PromptType.RESUME_ANALYSIS in self.claude_service.prompts
        assert PromptType.COVER_LETTER in self.claude_service.prompts
        assert PromptType.SKILLS_ANALYSIS in self.claude_service.prompts
    
    def test_prompt_templates(self):
        """Test prompt template content"""
        job_analysis_prompt = self.claude_service.prompts[PromptType.JOB_ANALYSIS]
        
        assert "{job_description}" in job_analysis_prompt
        assert "Job Summary" in job_analysis_prompt
        assert "Key Requirements" in job_analysis_prompt
        assert "JSON" in job_analysis_prompt
        
        cover_letter_prompt = self.claude_service.prompts[PromptType.COVER_LETTER]
        assert "{job_description}" in cover_letter_prompt
        assert "{company_info}" in cover_letter_prompt
        assert "{tone}" in cover_letter_prompt
    
    def test_rate_limiting_tracking(self):
        """Test rate limiting mechanisms"""
        # Test initial state
        stats = self.claude_service.get_usage_stats()
        assert stats['requests_last_minute'] == 0
        assert stats['tokens_last_minute'] == 0
        assert stats['requests_remaining'] == self.claude_service.REQUESTS_PER_MINUTE
        
        # Test recording usage
        self.claude_service._record_usage(100)
        stats = self.claude_service.get_usage_stats()
        assert stats['requests_last_minute'] == 1
        assert stats['tokens_last_minute'] == 100
    
    @pytest.mark.asyncio
    async def test_job_analysis_success(self):
        """Test successful job description analysis"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"job_title": "Software Engineer", "requirements": ["Python", "React"]}')]
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 200
        
        self.mock_async_client.messages.create = AsyncMock(return_value=mock_response)
        
        # Test job analysis
        result = await self.claude_service.analyze_job_description(
            job_description="Software Engineer position requiring Python and React experience."
        )
        
        assert isinstance(result, AnalysisResult)
        assert result.prompt_type == PromptType.JOB_ANALYSIS
        assert result.usage_tokens == 300
        assert "Software Engineer" in result.response_text
        
        # Verify API was called correctly
        self.mock_async_client.messages.create.assert_called_once()
        call_args = self.mock_async_client.messages.create.call_args
        assert call_args[1]['model'] == self.claude_service.DEFAULT_MODEL
        assert call_args[1]['max_tokens'] == self.claude_service.MAX_TOKENS
    
    @pytest.mark.asyncio
    async def test_job_analysis_validation(self):
        """Test job analysis input validation"""
        # Test empty job description
        with pytest.raises(ClaudeAPIError, match="at least 50 characters"):
            await self.claude_service.analyze_job_description("")
        
        # Test short job description
        with pytest.raises(ClaudeAPIError, match="at least 50 characters"):
            await self.claude_service.analyze_job_description("Short job")
    
    @pytest.mark.asyncio
    async def test_company_research_success(self):
        """Test successful company research"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"company_name": "TechCorp", "industry": "Software"}')]
        mock_response.usage.input_tokens = 80
        mock_response.usage.output_tokens = 150
        
        self.mock_async_client.messages.create = AsyncMock(return_value=mock_response)
        
        # Test company research
        result = await self.claude_service.research_company(
            company_name="TechCorp",
            context="Fast-growing startup in AI space"
        )
        
        assert isinstance(result, AnalysisResult)
        assert result.prompt_type == PromptType.COMPANY_RESEARCH
        assert "TechCorp" in result.response_text
    
    @pytest.mark.asyncio
    async def test_resume_analysis_success(self):
        """Test successful resume analysis"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"overall_score": 8, "strengths": ["Python experience"]}')]
        mock_response.usage.input_tokens = 200
        mock_response.usage.output_tokens = 300
        
        self.mock_async_client.messages.create = AsyncMock(return_value=mock_response)
        
        # Test resume analysis
        resume_content = "John Doe, Software Engineer with 5 years Python experience. Built web applications using Django and React. Led team of 3 developers."
        job_requirements = "Senior Software Engineer position requiring Python, Django, and team leadership experience."
        
        result = await self.claude_service.analyze_resume(
            resume_content=resume_content,
            job_requirements=job_requirements
        )
        
        assert isinstance(result, AnalysisResult)
        assert result.prompt_type == PromptType.RESUME_ANALYSIS
        assert "overall_score" in result.response_text
    
    @pytest.mark.asyncio
    async def test_cover_letter_generation(self):
        """Test cover letter generation"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='Dear Hiring Manager,\n\nI am excited to apply for the Software Engineer position...')]
        mock_response.usage.input_tokens = 150
        mock_response.usage.output_tokens = 250
        
        self.mock_async_client.messages.create = AsyncMock(return_value=mock_response)
        
        # Test cover letter generation
        result = await self.claude_service.generate_cover_letter(
            job_description="Software Engineer position at TechCorp",
            company_info="TechCorp is a fast-growing AI startup",
            resume_summary="Experienced Python developer with 5 years experience",
            tone="professional",
            focus_areas=["technical skills", "leadership experience"]
        )
        
        assert isinstance(result, AnalysisResult)
        assert result.prompt_type == PromptType.COVER_LETTER
        assert "Dear Hiring Manager" in result.response_text
    
    @pytest.mark.asyncio
    async def test_skills_gap_analysis(self):
        """Test skills gap analysis"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"missing_skills": ["React", "AWS"], "recommendations": ["Learn React fundamentals"]}')]
        mock_response.usage.input_tokens = 120
        mock_response.usage.output_tokens = 180
        
        self.mock_async_client.messages.create = AsyncMock(return_value=mock_response)
        
        # Test skills analysis
        result = await self.claude_service.analyze_skills_gap(
            current_skills=["Python", "Django", "PostgreSQL"],
            job_requirements="Full-stack developer with Python, React, and AWS experience",
            industry="Technology"
        )
        
        assert isinstance(result, AnalysisResult)
        assert result.prompt_type == PromptType.SKILLS_ANALYSIS
        assert "missing_skills" in result.response_text
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Test API error handling"""
        from anthropic import APIError
        
        # Mock API error
        self.mock_async_client.messages.create = AsyncMock(
            side_effect=APIError("API request failed")
        )
        
        # Test error handling
        with pytest.raises(ClaudeAPIError, match="API request failed"):
            await self.claude_service.analyze_job_description(
                "Software Engineer position with Python and React requirements for web development team."
            )
    
    @pytest.mark.asyncio
    async def test_streaming_analysis(self):
        """Test streaming analysis functionality"""
        # Mock streaming response
        async def mock_stream():
            chunks = [
                MagicMock(type="content_block_delta", delta=MagicMock(text="This is ")),
                MagicMock(type="content_block_delta", delta=MagicMock(text="a streaming ")),
                MagicMock(type="content_block_delta", delta=MagicMock(text="response.")),
                MagicMock(type="message_delta", usage=MagicMock(output_tokens=50))
            ]
            for chunk in chunks:
                yield chunk
        
        self.mock_async_client.messages.create = AsyncMock(return_value=mock_stream())
        
        # Test streaming
        chunks = []
        async for chunk in self.claude_service.stream_analysis(
            "Analyze this job description",
            PromptType.JOB_ANALYSIS
        ):
            chunks.append(chunk)
        
        assert chunks == ["This is ", "a streaming ", "response."]
    
    def test_singleton_pattern(self):
        """Test Claude service singleton pattern"""
        with patch('services.claude_service.get_config'):
            service1 = get_claude_service()
            service2 = get_claude_service()
            assert service1 is service2


class TestPromptFormatting:
    """Test prompt template formatting"""
    
    def setup_method(self):
        """Setup test environment"""
        with patch('services.claude_service.get_config'):
            self.claude_service = ClaudeService()
    
    def test_job_analysis_prompt_formatting(self):
        """Test job analysis prompt formatting"""
        job_desc = "Software Engineer position requiring Python and React"
        prompt = self.claude_service.prompts[PromptType.JOB_ANALYSIS]
        formatted = prompt.format(job_description=job_desc)
        
        assert job_desc in formatted
        assert "Job Summary" in formatted
        assert "Key Requirements" in formatted
    
    def test_cover_letter_prompt_formatting(self):
        """Test cover letter prompt formatting"""
        prompt = self.claude_service.prompts[PromptType.COVER_LETTER]
        formatted = prompt.format(
            job_description="Software Engineer at TechCorp",
            company_info="Fast-growing AI startup",
            resume_summary="5 years Python experience",
            tone="professional",
            focus_areas="technical skills, leadership"
        )
        
        assert "Software Engineer at TechCorp" in formatted
        assert "Fast-growing AI startup" in formatted
        assert "professional" in formatted
        assert "technical skills, leadership" in formatted


class TestIntegration:
    """Integration tests for Claude service"""
    
    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self):
        """Test complete analysis workflow"""
        with patch('services.claude_service.get_config'), \
             patch('services.claude_service.Anthropic'), \
             patch('services.claude_service.AsyncAnthropic') as mock_async:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_async.return_value = mock_client
            
            # Mock responses for different analysis types
            mock_responses = {
                'job': MagicMock(
                    content=[MagicMock(text='{"job_title": "Software Engineer"}')],
                    usage=MagicMock(input_tokens=100, output_tokens=200)
                ),
                'company': MagicMock(
                    content=[MagicMock(text='{"company_name": "TechCorp"}')],
                    usage=MagicMock(input_tokens=80, output_tokens=150)
                ),
                'resume': MagicMock(
                    content=[MagicMock(text='{"score": 8}')],
                    usage=MagicMock(input_tokens=200, output_tokens=300)
                )
            }
            
            # Configure mock to return different responses
            call_count = 0
            async def mock_create(*args, **kwargs):
                nonlocal call_count
                responses = ['job', 'company', 'resume']
                response = mock_responses[responses[call_count]]
                call_count += 1
                return response
            
            mock_client.messages.create = AsyncMock(side_effect=mock_create)
            
            # Create service
            service = ClaudeService()
            
            # Test workflow
            job_result = await service.analyze_job_description(
                "Software Engineer position requiring Python and React experience for building web applications."
            )
            assert job_result.prompt_type == PromptType.JOB_ANALYSIS
            
            company_result = await service.research_company("TechCorp")
            assert company_result.prompt_type == PromptType.COMPANY_RESEARCH
            
            resume_result = await service.analyze_resume(
                "John Doe, Software Engineer with Python and React experience. Built multiple web applications.",
                "Senior Software Engineer requiring Python, React, and web development experience."
            )
            assert resume_result.prompt_type == PromptType.RESUME_ANALYSIS


if __name__ == "__main__":
    # Simple test runner for development
    import sys
    
    print("Running Claude service tests...")
    
    try:
        # Mock configuration for standalone tests
        with patch('services.claude_service.get_config') as mock_config, \
             patch('services.claude_service.Anthropic'), \
             patch('services.claude_service.AsyncAnthropic'):
            
            mock_claude_config = MagicMock()
            mock_claude_config.api_key = "test-api-key"
            mock_config.return_value.claude = mock_claude_config
            
            # Test service initialization
            service = ClaudeService()
            print("✓ ClaudeService initialization: PASS")
            
            # Test prompt templates
            assert PromptType.JOB_ANALYSIS in service.prompts
            assert "{job_description}" in service.prompts[PromptType.JOB_ANALYSIS]
            print("✓ Prompt templates loading: PASS")
            
            # Test usage stats
            stats = service.get_usage_stats()
            assert 'requests_last_minute' in stats
            assert 'tokens_last_minute' in stats
            print("✓ Usage statistics: PASS")
            
            # Test rate limiting
            service._record_usage(100)
            stats = service.get_usage_stats()
            assert stats['requests_last_minute'] == 1
            assert stats['tokens_last_minute'] == 100
            print("✓ Rate limiting tracking: PASS")
            
            # Test singleton
            service1 = get_claude_service()
            service2 = get_claude_service()
            assert service1 is service2
            print("✓ Singleton pattern: PASS")
        
        print("\n✅ All Claude service tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)