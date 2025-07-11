"""
Claude API Integration Service

Handles communication with Anthropic's Claude API for job analysis,
company research, and resume enhancement tasks.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import json
import time

import anthropic
from anthropic import Anthropic, AsyncAnthropic
from anthropic.types import MessageParam

from config import get_config

logger = logging.getLogger(__name__)


class PromptType(Enum):
    """Types of prompts for different analysis tasks"""
    JOB_ANALYSIS = "job_analysis"
    COMPANY_RESEARCH = "company_research"
    RESUME_ANALYSIS = "resume_analysis"
    COVER_LETTER = "cover_letter"
    SKILLS_ANALYSIS = "skills_analysis"


@dataclass
class AnalysisResult:
    """Result from Claude API analysis"""
    prompt_type: PromptType
    response_text: str
    usage_tokens: int
    processing_time: float
    metadata: Dict[str, Any]


class ClaudeAPIError(Exception):
    """Raised when Claude API encounters an error"""
    pass


class ClaudeService:
    """Service for interacting with Claude API"""
    
    # Model configuration
    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
    MAX_TOKENS = 4000
    TEMPERATURE = 0.7
    
    # Rate limiting
    REQUESTS_PER_MINUTE = 50
    TOKENS_PER_MINUTE = 40000
    
    def __init__(self):
        """Initialize Claude service"""
        self.config = get_config()
        
        # Initialize clients
        try:
            self.sync_client = Anthropic(api_key=self.config.claude.api_key)
            self.async_client = AsyncAnthropic(api_key=self.config.claude.api_key)
        except Exception as e:
            logger.error(f"Failed to initialize Claude clients: {e}")
            raise ClaudeAPIError(f"Claude API initialization failed: {e}")
        
        # Rate limiting tracking
        self._request_times = []
        self._token_usage = []
        
        # Load prompt templates
        self.prompts = self._load_prompt_templates()
    
    def _load_prompt_templates(self) -> Dict[PromptType, str]:
        """Load prompt templates for different analysis types"""
        return {
            PromptType.JOB_ANALYSIS: """
You are an expert job market analyst. Analyze the following job description and extract key information in a structured format.

Job Description:
{job_description}

Please provide a comprehensive analysis including:

1. **Job Summary**:
   - Job title
   - Company name (if mentioned)
   - Location
   - Employment type (full-time, part-time, contract, etc.)
   - Experience level required

2. **Key Requirements**:
   - Required skills and technologies
   - Educational requirements
   - Years of experience needed
   - Certifications or licenses required

3. **Responsibilities**:
   - Main job duties and responsibilities
   - Team collaboration requirements
   - Leadership expectations

4. **Preferred Qualifications**:
   - Nice-to-have skills
   - Preferred experience
   - Additional qualifications

5. **Compensation & Benefits**:
   - Salary range (if mentioned)
   - Benefits mentioned
   - Remote work options

6. **Keywords for ATS**:
   - Important keywords that should appear in a resume
   - Industry-specific terms
   - Technical terminology

Format your response as a JSON object with clear sections. Be thorough but concise.
""",

            PromptType.COMPANY_RESEARCH: """
You are a business research specialist. Based on the company information provided, create a comprehensive company profile.

Company Name: {company_name}
Additional Context: {context}

Please research and provide:

1. **Company Overview**:
   - Industry and sector
   - Company size and stage
   - Headquarters location
   - Brief company history

2. **Business Model**:
   - Primary products/services
   - Target customers
   - Revenue model
   - Key differentiators

3. **Company Culture**:
   - Values and mission
   - Work environment
   - Employee benefits
   - Diversity and inclusion initiatives

4. **Recent News & Developments**:
   - Recent funding or acquisitions
   - Product launches
   - Market expansion
   - Leadership changes

5. **Industry Position**:
   - Competitors
   - Market share
   - Growth trends
   - Challenges facing the company

6. **Employee Insights**:
   - What employees say about working there
   - Career development opportunities
   - Work-life balance
   - Common interview topics

Format as a JSON object. If specific information isn't available, indicate that clearly.
""",

            PromptType.RESUME_ANALYSIS: """
You are a professional resume consultant and career advisor. Analyze the provided resume against the job requirements and provide comprehensive feedback.

Resume Content:
{resume_content}

Job Requirements:
{job_requirements}

Please provide:

1. **Overall Assessment**:
   - Resume strength score (1-10)
   - Job match percentage
   - Key strengths
   - Major weaknesses

2. **Skills Analysis**:
   - Skills that match job requirements
   - Missing critical skills
   - Skills to emphasize more
   - Skills to add or learn

3. **Experience Alignment**:
   - Relevant experience highlights
   - Experience gaps
   - How to better position experience
   - Quantifiable achievements to add

4. **Resume Structure & Content**:
   - Section organization feedback
   - Content suggestions
   - Formatting recommendations
   - Length and clarity assessment

5. **ATS Optimization**:
   - Keywords to add
   - Formatting issues for ATS
   - Section headers to improve
   - File format recommendations

6. **Improvement Recommendations**:
   - Top 5 priority changes
   - Quick wins for immediate improvement
   - Long-term skill development suggestions
   - Industry-specific advice

Format as a JSON object with actionable recommendations.
""",

            PromptType.COVER_LETTER: """
You are an expert cover letter writer with extensive experience in various industries. Create a compelling, personalized cover letter.

Job Description:
{job_description}

Company Information:
{company_info}

Candidate Resume Summary:
{resume_summary}

Tone Preference: {tone}
Focus Areas: {focus_areas}

Create a cover letter that:

1. **Opening**: Strong, attention-grabbing introduction that shows genuine interest
2. **Body Paragraphs**: 
   - Highlight most relevant experience and achievements
   - Demonstrate knowledge of the company and role
   - Show cultural fit and enthusiasm
   - Address any potential concerns proactively
3. **Closing**: Professional conclusion with clear next steps

Requirements:
- Keep it to 3-4 paragraphs
- Use the specified tone ({tone})
- Focus on {focus_areas}
- Include specific examples and metrics when possible
- Avoid generic phrases
- Make it scannable with good structure
- Ensure it complements the resume without repeating it

Provide both the cover letter text and a brief analysis of the approach taken.
""",

            PromptType.SKILLS_ANALYSIS: """
You are a skills assessment expert and career development specialist. Analyze the skills gap between current capabilities and job requirements.

Current Skills (from resume):
{current_skills}

Job Requirements:
{job_requirements}

Industry Context:
{industry}

Please provide:

1. **Skills Inventory**:
   - Technical skills present
   - Soft skills demonstrated
   - Certifications and credentials
   - Experience level assessment

2. **Gap Analysis**:
   - Critical missing skills
   - Skills that need strengthening
   - Nice-to-have skills absent
   - Transferable skills identification

3. **Learning Priorities**:
   - High-impact skills to learn first
   - Quick wins for skill building
   - Long-term development goals
   - Industry trend considerations

4. **Skill Development Plan**:
   - Recommended courses or certifications
   - Practice projects to build skills
   - Timeline for skill acquisition
   - Resources for learning

5. **Resume Enhancement**:
   - How to better showcase existing skills
   - Skills to emphasize more prominently
   - Ways to demonstrate proficiency
   - Keywords to include

Format as a JSON object with specific, actionable recommendations.
"""
        }
    
    def _check_rate_limits(self) -> None:
        """Check and enforce rate limits"""
        current_time = time.time()
        
        # Clean old entries (older than 1 minute)
        cutoff_time = current_time - 60
        old_request_count = len(self._request_times)
        old_token_entries = len(self._token_usage)
        
        self._request_times = [t for t in self._request_times if t > cutoff_time]
        self._token_usage = [(t, tokens) for t, tokens in self._token_usage if t > cutoff_time]
        
        cleaned_requests = old_request_count - len(self._request_times)
        cleaned_tokens = old_token_entries - len(self._token_usage)
        
        if cleaned_requests > 0 or cleaned_tokens > 0:
            print(f"🧹 [CLAUDE API] Cleaned old rate limit entries: {cleaned_requests} requests, {cleaned_tokens} token entries")
        
        # Check request rate limit
        current_requests = len(self._request_times)
        print(f"📈 [CLAUDE API] Current rate limits: {current_requests}/{self.REQUESTS_PER_MINUTE} requests per minute")
        
        if current_requests >= self.REQUESTS_PER_MINUTE:
            sleep_time = 60 - (current_time - self._request_times[0])
            if sleep_time > 0:
                print(f"⏳ [CLAUDE API] REQUEST RATE LIMIT: Sleeping for {sleep_time:.1f} seconds...")
                logger.warning(f"Rate limit reached, sleeping for {sleep_time:.1f} seconds")
                time.sleep(sleep_time)
                print(f"✅ [CLAUDE API] Rate limit wait completed")
        
        # Check token rate limit
        total_tokens = sum(tokens for _, tokens in self._token_usage)
        print(f"📈 [CLAUDE API] Current token usage: {total_tokens}/{self.TOKENS_PER_MINUTE} tokens per minute")
        
        if total_tokens >= self.TOKENS_PER_MINUTE:
            oldest_time = self._token_usage[0][0] if self._token_usage else current_time
            sleep_time = 60 - (current_time - oldest_time)
            if sleep_time > 0:
                print(f"⏳ [CLAUDE API] TOKEN RATE LIMIT: Sleeping for {sleep_time:.1f} seconds...")
                logger.warning(f"Token rate limit reached, sleeping for {sleep_time:.1f} seconds")
                time.sleep(sleep_time)
                print(f"✅ [CLAUDE API] Token rate limit wait completed")
    
    def _record_usage(self, tokens_used: int) -> None:
        """Record API usage for rate limiting"""
        current_time = time.time()
        self._request_times.append(current_time)
        self._token_usage.append((current_time, tokens_used))
    
    async def analyze_job_description(
        self,
        job_description: str,
        additional_context: Optional[str] = None
    ) -> AnalysisResult:
        """
        Analyze a job description using Claude API.
        
        Args:
            job_description: The job posting text
            additional_context: Optional additional context
            
        Returns:
            AnalysisResult with structured job analysis
        """
        print(f"\n🔍 [CLAUDE API] ==================== JOB DESCRIPTION ANALYSIS ====================")
        print(f"📝 [CLAUDE API] Input length: {len(job_description)} characters")
        print(f"💡 [CLAUDE API] Additional context: {'Yes' if additional_context else 'None'}")
        
        if not job_description or len(job_description.strip()) < 50:
            print(f"❌ [CLAUDE API] ERROR: Job description too short ({len(job_description.strip())} chars, minimum 50)")
            raise ClaudeAPIError("Job description must be at least 50 characters long")
        
        print(f"📋 [CLAUDE API] Preparing job analysis prompt...")
        print(f"🎯 [CLAUDE API] Using model: {self.DEFAULT_MODEL}")
        print(f"🔧 [CLAUDE API] Max tokens: {self.MAX_TOKENS}, Temperature: {self.TEMPERATURE}")
        
        prompt = self.prompts[PromptType.JOB_ANALYSIS].format(
            job_description=job_description
        )
        
        print(f"📤 [CLAUDE API] Sending request to Claude API...")
        
        return await self._make_api_call(
            prompt=prompt,
            prompt_type=PromptType.JOB_ANALYSIS,
            context={"job_description_length": len(job_description)}
        )
    
    async def research_company(
        self,
        company_name: str,
        context: Optional[str] = None
    ) -> AnalysisResult:
        """
        Research company information using Claude API.
        
        Args:
            company_name: Name of the company
            context: Additional context about the company
            
        Returns:
            AnalysisResult with company research
        """
        print(f"\n🏢 [CLAUDE API] ==================== COMPANY RESEARCH ====================")
        print(f"🏆 [CLAUDE API] Company name: '{company_name}'")
        print(f"📚 [CLAUDE API] Additional context: {'Yes' if context else 'None'}")
        
        if not company_name or len(company_name.strip()) < 2:
            print(f"❌ [CLAUDE API] ERROR: Company name too short ('{company_name}', minimum 2 characters)")
            raise ClaudeAPIError("Company name is required")
        
        print(f"📋 [CLAUDE API] Preparing company research prompt...")
        print(f"🎯 [CLAUDE API] Using model: {self.DEFAULT_MODEL}")
        print(f"🔧 [CLAUDE API] Max tokens: {self.MAX_TOKENS}, Temperature: {self.TEMPERATURE}")
        
        prompt = self.prompts[PromptType.COMPANY_RESEARCH].format(
            company_name=company_name,
            context=context or "No additional context provided"
        )
        
        print(f"📤 [CLAUDE API] Sending company research request to Claude API...")
        
        return await self._make_api_call(
            prompt=prompt,
            prompt_type=PromptType.COMPANY_RESEARCH,
            context={"company_name": company_name}
        )
    
    async def analyze_resume(
        self,
        resume_content: str,
        job_requirements: str
    ) -> AnalysisResult:
        """
        Analyze resume against job requirements.
        
        Args:
            resume_content: Extracted resume text
            job_requirements: Job requirements from job analysis
            
        Returns:
            AnalysisResult with resume analysis
        """
        print(f"\n📄 [CLAUDE API] ==================== RESUME ANALYSIS ====================")
        print(f"📝 [CLAUDE API] Resume content length: {len(resume_content)} characters")
        print(f"📋 [CLAUDE API] Job requirements length: {len(job_requirements)} characters")
        
        if not resume_content or len(resume_content.strip()) < 100:
            print(f"❌ [CLAUDE API] ERROR: Resume content too short ({len(resume_content.strip())} chars, minimum 100)")
            raise ClaudeAPIError("Resume content must be at least 100 characters long")
        
        if not job_requirements:
            print(f"❌ [CLAUDE API] ERROR: Job requirements are missing")
            raise ClaudeAPIError("Job requirements are required")
        
        print(f"📋 [CLAUDE API] Preparing resume analysis prompt...")
        print(f"🎯 [CLAUDE API] Using model: {self.DEFAULT_MODEL}")
        print(f"🔧 [CLAUDE API] Max tokens: {self.MAX_TOKENS}, Temperature: {self.TEMPERATURE}")
        
        prompt = self.prompts[PromptType.RESUME_ANALYSIS].format(
            resume_content=resume_content,
            job_requirements=job_requirements
        )
        
        print(f"📤 [CLAUDE API] Sending resume analysis request to Claude API...")
        
        return await self._make_api_call(
            prompt=prompt,
            prompt_type=PromptType.RESUME_ANALYSIS,
            context={
                "resume_length": len(resume_content),
                "requirements_length": len(job_requirements)
            }
        )
    
    async def generate_cover_letter(
        self,
        job_description: str,
        company_info: str,
        resume_summary: str,
        tone: str = "professional",
        focus_areas: Optional[List[str]] = None
    ) -> AnalysisResult:
        """
        Generate personalized cover letter.
        
        Args:
            job_description: Job posting details
            company_info: Company research information
            resume_summary: Summary of candidate's background
            tone: Writing tone (professional, conversational, etc.)
            focus_areas: Areas to emphasize
            
        Returns:
            AnalysisResult with generated cover letter
        """
        print(f"\n✉️ [CLAUDE API] ==================== COVER LETTER GENERATION ====================")
        print(f"📝 [CLAUDE API] Job description length: {len(job_description)} characters")
        print(f"🏢 [CLAUDE API] Company info length: {len(company_info)} characters")
        print(f"📄 [CLAUDE API] Resume summary length: {len(resume_summary)} characters")
        print(f"🎨 [CLAUDE API] Tone: {tone}")
        
        focus_list = focus_areas or ["relevant experience", "technical skills"]
        focus_str = ", ".join(focus_list)
        print(f"🎯 [CLAUDE API] Focus areas: {focus_str}")
        
        print(f"📋 [CLAUDE API] Preparing cover letter generation prompt...")
        print(f"🎯 [CLAUDE API] Using model: {self.DEFAULT_MODEL}")
        print(f"🔧 [CLAUDE API] Max tokens: {self.MAX_TOKENS}, Temperature: {self.TEMPERATURE}")
        
        prompt = self.prompts[PromptType.COVER_LETTER].format(
            job_description=job_description,
            company_info=company_info,
            resume_summary=resume_summary,
            tone=tone,
            focus_areas=focus_str
        )
        
        print(f"📤 [CLAUDE API] Sending cover letter generation request to Claude API...")
        
        return await self._make_api_call(
            prompt=prompt,
            prompt_type=PromptType.COVER_LETTER,
            context={
                "tone": tone,
                "focus_areas": focus_list
            }
        )
    
    async def analyze_skills_gap(
        self,
        current_skills: List[str],
        job_requirements: str,
        industry: str
    ) -> AnalysisResult:
        """
        Analyze skills gap and provide development recommendations.
        
        Args:
            current_skills: List of current skills from resume
            job_requirements: Job requirements text
            industry: Industry context
            
        Returns:
            AnalysisResult with skills analysis
        """
        print(f"\n🎯 [CLAUDE API] ==================== SKILLS GAP ANALYSIS ====================")
        print(f"🛠️ [CLAUDE API] Current skills count: {len(current_skills)}")
        print(f"📋 [CLAUDE API] Job requirements length: {len(job_requirements)} characters")
        print(f"🏭 [CLAUDE API] Industry: {industry}")
        
        skills_str = ", ".join(current_skills) if current_skills else "No skills specified"
        if current_skills:
            print(f"🔧 [CLAUDE API] Skills preview: {skills_str[:100]}{'...' if len(skills_str) > 100 else ''}")
        else:
            print(f"⚠️ [CLAUDE API] WARNING: No current skills provided")
        
        print(f"📋 [CLAUDE API] Preparing skills gap analysis prompt...")
        print(f"🎯 [CLAUDE API] Using model: {self.DEFAULT_MODEL}")
        print(f"🔧 [CLAUDE API] Max tokens: {self.MAX_TOKENS}, Temperature: {self.TEMPERATURE}")
        
        prompt = self.prompts[PromptType.SKILLS_ANALYSIS].format(
            current_skills=skills_str,
            job_requirements=job_requirements,
            industry=industry
        )
        
        print(f"📤 [CLAUDE API] Sending skills gap analysis request to Claude API...")
        
        return await self._make_api_call(
            prompt=prompt,
            prompt_type=PromptType.SKILLS_ANALYSIS,
            context={
                "skills_count": len(current_skills),
                "industry": industry
            }
        )
    
    async def _make_api_call(
        self,
        prompt: str,
        prompt_type: PromptType,
        context: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """
        Make API call to Claude with error handling and rate limiting.
        
        Args:
            prompt: The prompt to send
            prompt_type: Type of analysis being performed
            context: Additional context for the request
            
        Returns:
            AnalysisResult with API response
        """
        print(f"\n🚀 [CLAUDE API] ==================== API CALL EXECUTION ====================")
        print(f"💬 [CLAUDE API] Prompt type: {prompt_type.value}")
        print(f"📝 [CLAUDE API] Prompt length: {len(prompt)} characters")
        print(f"📈 [CLAUDE API] Context data: {list(context.keys()) if context else 'None'}")
        
        # Check rate limits
        print(f"🕒 [CLAUDE API] Checking rate limits...")
        self._check_rate_limits()
        print(f"✅ [CLAUDE API] Rate limits OK - proceeding with request")
        
        start_time = time.time()
        print(f"⏱️ [CLAUDE API] Request started at: {time.strftime('%H:%M:%S', time.localtime(start_time))}")
        
        try:
            # Prepare messages
            print(f"📦 [CLAUDE API] Preparing message payload...")
            messages: List[MessageParam] = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            print(f"✅ [CLAUDE API] Message payload prepared successfully")
            
            # Make API call
            print(f"🌐 [CLAUDE API] Sending request to Anthropic API...")
            print(f"🤖 [CLAUDE API] Model: {self.DEFAULT_MODEL}")
            print(f"🔢 [CLAUDE API] Max tokens: {self.MAX_TOKENS}")
            print(f"🌡️ [CLAUDE API] Temperature: {self.TEMPERATURE}")
            
            response = await self.async_client.messages.create(
                model=self.DEFAULT_MODEL,
                max_tokens=self.MAX_TOKENS,
                temperature=self.TEMPERATURE,
                messages=messages
            )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            print(f"✅ [CLAUDE API] API response received successfully!")
            print(f"⏱️ [CLAUDE API] Processing time: {processing_time:.2f} seconds")
            
            # Extract response text
            print(f"🔄 [CLAUDE API] Extracting response content...")
            response_text = ""
            if response.content:
                for block in response.content:
                    if hasattr(block, 'text'):
                        response_text += block.text
            
            print(f"📝 [CLAUDE API] Response length: {len(response_text)} characters")
            
            # Record usage
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            print(f"📊 [CLAUDE API] Token usage:")
            print(f"    • Input tokens: {response.usage.input_tokens}")
            print(f"    • Output tokens: {response.usage.output_tokens}")
            print(f"    • Total tokens: {tokens_used}")
            
            self._record_usage(tokens_used)
            print(f"📈 [CLAUDE API] Usage recorded for rate limiting")
            
            logger.info(f"Claude API call successful: {prompt_type.value}, {tokens_used} tokens, {processing_time:.2f}s")
            print(f"✅ [CLAUDE API] ==================== API CALL COMPLETED SUCCESSFULLY ====================")
            
            return AnalysisResult(
                prompt_type=prompt_type,
                response_text=response_text,
                usage_tokens=tokens_used,
                processing_time=processing_time,
                metadata={
                    "model": self.DEFAULT_MODEL,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "context": context or {}
                }
            )
            
        except anthropic.APIError as e:
            error_msg = f"API request failed: {e}"
            print(f"❌ [CLAUDE API] ERROR: Anthropic API error - {e}")
            logger.error(f"Claude API error: {e}")
            raise ClaudeAPIError(error_msg)
        except anthropic.RateLimitError as e:
            error_msg = f"Rate limit exceeded: {e}"
            print(f"❌ [CLAUDE API] ERROR: Rate limit exceeded - {e}")
            print(f"⏳ [CLAUDE API] You may need to wait before making more requests")
            logger.error(f"Claude API rate limit exceeded: {e}")
            raise ClaudeAPIError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(f"❌ [CLAUDE API] ERROR: Unexpected error - {e}")
            print(f"🔍 [CLAUDE API] Error type: {type(e).__name__}")
            logger.error(f"Unexpected error in Claude API call: {e}")
            raise ClaudeAPIError(error_msg)
    
    async def stream_analysis(
        self,
        prompt: str,
        prompt_type: PromptType
    ) -> AsyncGenerator[str, None]:
        """
        Stream Claude API response for real-time updates.
        
        Args:
            prompt: The prompt to send
            prompt_type: Type of analysis
            
        Yields:
            Chunks of response text
        """
        # Check rate limits
        self._check_rate_limits()
        
        try:
            messages: List[MessageParam] = [
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            # Create streaming response
            stream = await self.async_client.messages.create(
                model=self.DEFAULT_MODEL,
                max_tokens=self.MAX_TOKENS,
                temperature=self.TEMPERATURE,
                messages=messages,
                stream=True
            )
            
            total_tokens = 0
            async for chunk in stream:
                if chunk.type == "content_block_delta":
                    if hasattr(chunk.delta, 'text'):
                        yield chunk.delta.text
                elif chunk.type == "message_delta":
                    if chunk.usage:
                        total_tokens += chunk.usage.output_tokens
            
            # Record usage
            self._record_usage(total_tokens)
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            raise ClaudeAPIError(f"Streaming failed: {e}")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        current_time = time.time()
        cutoff_time = current_time - 60
        
        recent_requests = len([t for t in self._request_times if t > cutoff_time])
        recent_tokens = sum(tokens for t, tokens in self._token_usage if t > cutoff_time)
        
        return {
            "requests_last_minute": recent_requests,
            "tokens_last_minute": recent_tokens,
            "requests_limit": self.REQUESTS_PER_MINUTE,
            "tokens_limit": self.TOKENS_PER_MINUTE,
            "requests_remaining": max(0, self.REQUESTS_PER_MINUTE - recent_requests),
            "tokens_remaining": max(0, self.TOKENS_PER_MINUTE - recent_tokens)
        }


# Global service instance
_claude_service_instance = None

def get_claude_service() -> ClaudeService:
    """Get Claude service singleton instance"""
    global _claude_service_instance
    if _claude_service_instance is None:
        _claude_service_instance = ClaudeService()
    return _claude_service_instance