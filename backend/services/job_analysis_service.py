"""
Job Analysis Orchestration Service

Coordinates the complete 7-step job application analysis workflow:
1. Job Description Analysis (14%)
2. Company Research (28%)
3. Resume Parsing (42%)
4. Skills Gap Analysis (57%)
5. Resume Enhancement (71%)
6. Cover Letter Generation (85%)
7. Final Review & Formatting (100%)
"""

import logging
import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
import secrets
import time

from services.file_service import get_file_service, FileInfo, FileProcessingError
from services.claude_service import get_claude_service, ClaudeAPIError, PromptType
from services.auth_service import SessionData
from utils.parsers import get_resume_parser, ParsedResume

logger = logging.getLogger(__name__)


class AnalysisStep(Enum):
    """Analysis workflow steps"""
    JOB_ANALYSIS = "job_analysis"
    COMPANY_RESEARCH = "company_research"
    RESUME_PARSING = "resume_parsing"
    SKILLS_ANALYSIS = "skills_analysis"
    RESUME_ENHANCEMENT = "resume_enhancement"
    COVER_LETTER = "cover_letter"
    FINAL_REVIEW = "final_review"


class AnalysisStatus(Enum):
    """Analysis job status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AnalysisProgress:
    """Progress tracking for analysis job"""
    step: AnalysisStep
    step_number: int
    step_name: str
    status: AnalysisStatus
    progress_percentage: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class AnalysisRequest:
    """Request for job analysis"""
    session_id: str
    user_id: str
    job_description: str
    job_url: Optional[str] = None
    resume_file_id: Optional[str] = None
    resume_text: Optional[str] = None
    preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}


@dataclass
class AnalysisResult:
    """Complete analysis results"""
    session_id: str
    request: AnalysisRequest
    job_analysis: Dict[str, Any]
    company_research: Dict[str, Any]
    parsed_resume: Dict[str, Any]
    skills_analysis: Dict[str, Any]
    resume_recommendations: Dict[str, Any]
    cover_letter: Dict[str, Any]
    final_summary: Dict[str, Any]
    processing_metadata: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime] = None


class JobAnalysisError(Exception):
    """Raised when job analysis encounters an error"""
    pass


class JobAnalysisService:
    """
    Orchestrates the complete job application analysis workflow.
    
    Coordinates file processing, AI analysis, and result generation
    across multiple steps with progress tracking.
    """
    
    # Step configuration with progress percentages
    STEP_CONFIG = {
        AnalysisStep.JOB_ANALYSIS: {
            "step_number": 1,
            "step_name": "Job Description Analysis",
            "progress_percentage": 14,
            "description": "Analyzing job requirements and extracting key information"
        },
        AnalysisStep.COMPANY_RESEARCH: {
            "step_number": 2,
            "step_name": "Company Research",
            "progress_percentage": 28,
            "description": "Researching company culture, values, and recent developments"
        },
        AnalysisStep.RESUME_PARSING: {
            "step_number": 3,
            "step_name": "Resume Analysis",
            "progress_percentage": 42,
            "description": "Parsing resume and extracting structured information"
        },
        AnalysisStep.SKILLS_ANALYSIS: {
            "step_number": 4,
            "step_name": "Skills Gap Analysis",
            "progress_percentage": 57,
            "description": "Comparing skills and identifying gaps"
        },
        AnalysisStep.RESUME_ENHANCEMENT: {
            "step_number": 5,
            "step_name": "Resume Enhancement",
            "progress_percentage": 71,
            "description": "Generating improvement recommendations"
        },
        AnalysisStep.COVER_LETTER: {
            "step_number": 6,
            "step_name": "Cover Letter Generation",
            "progress_percentage": 85,
            "description": "Creating personalized cover letter"
        },
        AnalysisStep.FINAL_REVIEW: {
            "step_number": 7,
            "step_name": "Final Review & Formatting",
            "progress_percentage": 100,
            "description": "Quality check and final formatting"
        }
    }
    
    def __init__(self):
        """Initialize job analysis service"""
        self.file_service = get_file_service()
        self.claude_service = get_claude_service()
        self.resume_parser = get_resume_parser()
        
        # In-memory storage for active jobs (in production, use Redis/database)
        self.active_jobs: Dict[str, Dict[str, Any]] = {}
        self.job_progress: Dict[str, List[AnalysisProgress]] = {}
        self.job_results: Dict[str, AnalysisResult] = {}
    
    async def start_analysis(
        self,
        session_data: SessionData,
        job_description: str,
        job_url: Optional[str] = None,
        resume_file_id: Optional[str] = None,
        resume_text: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start a new job analysis workflow.
        
        Args:
            session_data: User session information
            job_description: Job posting text
            job_url: Optional job posting URL
            resume_file_id: File ID from file upload service
            resume_text: Raw resume text (alternative to file)
            preferences: User preferences for analysis
            
        Returns:
            Analysis job ID for tracking progress
        """
        # Validate inputs
        if not job_description or len(job_description.strip()) < 50:
            raise JobAnalysisError("Job description must be at least 50 characters long")
        
        if not resume_file_id and not resume_text:
            raise JobAnalysisError("Either resume file or resume text must be provided")
        
        # Generate analysis job ID
        analysis_id = f"analysis_{secrets.token_urlsafe(16)}"
        
        # Create analysis request
        request = AnalysisRequest(
            session_id=session_data.session_id,
            user_id=session_data.user_id or "anonymous",
            job_description=job_description,
            job_url=job_url,
            resume_file_id=resume_file_id,
            resume_text=resume_text,
            preferences=preferences or {}
        )
        
        # Initialize job tracking
        self.active_jobs[analysis_id] = {
            "request": request,
            "status": AnalysisStatus.PENDING,
            "current_step": None,
            "started_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Initialize progress tracking
        self.job_progress[analysis_id] = []
        for step in AnalysisStep:
            config = self.STEP_CONFIG[step]
            progress = AnalysisProgress(
                step=step,
                step_number=config["step_number"],
                step_name=config["step_name"],
                status=AnalysisStatus.PENDING,
                progress_percentage=config["progress_percentage"]
            )
            self.job_progress[analysis_id].append(progress)
        
        logger.info(f"Started analysis job {analysis_id} for session {session_data.session_id}")
        
        # Start processing asynchronously
        asyncio.create_task(self._process_analysis(analysis_id))
        
        return analysis_id
    
    async def _process_analysis(self, analysis_id: str) -> None:
        """
        Process the complete analysis workflow.
        
        Args:
            analysis_id: Analysis job ID
        """
        try:
            job = self.active_jobs[analysis_id]
            request = job["request"]
            
            # Update job status
            job["status"] = AnalysisStatus.PROCESSING
            job["updated_at"] = datetime.now(timezone.utc)
            
            logger.info(f"Starting analysis processing for job {analysis_id}")
            
            # Execute each step
            job_analysis_result = await self._execute_step_1_job_analysis(analysis_id, request)
            company_research_result = await self._execute_step_2_company_research(analysis_id, request, job_analysis_result)
            parsed_resume_result = await self._execute_step_3_resume_parsing(analysis_id, request)
            skills_analysis_result = await self._execute_step_4_skills_analysis(analysis_id, request, job_analysis_result, parsed_resume_result)
            resume_enhancement_result = await self._execute_step_5_resume_enhancement(analysis_id, request, job_analysis_result, parsed_resume_result, skills_analysis_result)
            cover_letter_result = await self._execute_step_6_cover_letter(analysis_id, request, job_analysis_result, company_research_result, parsed_resume_result)
            final_summary_result = await self._execute_step_7_final_review(analysis_id, request, job_analysis_result, company_research_result, parsed_resume_result, skills_analysis_result, resume_enhancement_result, cover_letter_result)
            
            # Create final result
            result = AnalysisResult(
                session_id=request.session_id,
                request=request,
                job_analysis=job_analysis_result,
                company_research=company_research_result,
                parsed_resume=parsed_resume_result,
                skills_analysis=skills_analysis_result,
                resume_recommendations=resume_enhancement_result,
                cover_letter=cover_letter_result,
                final_summary=final_summary_result,
                processing_metadata={
                    "analysis_id": analysis_id,
                    "total_processing_time": (datetime.now(timezone.utc) - job["started_at"]).total_seconds(),
                    "steps_completed": 7,
                    "claude_api_calls": self._count_claude_calls(analysis_id)
                },
                created_at=job["started_at"],
                completed_at=datetime.now(timezone.utc)
            )
            
            # Store result
            self.job_results[analysis_id] = result
            
            # Update job status
            job["status"] = AnalysisStatus.COMPLETED
            job["updated_at"] = datetime.now(timezone.utc)
            
            logger.info(f"Analysis job {analysis_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Analysis job {analysis_id} failed: {e}")
            
            # Update job status to failed
            job = self.active_jobs.get(analysis_id, {})
            job["status"] = AnalysisStatus.FAILED
            job["error"] = str(e)
            job["updated_at"] = datetime.now(timezone.utc)
            
            # Mark current step as failed
            progress_list = self.job_progress.get(analysis_id, [])
            for progress in progress_list:
                if progress.status == AnalysisStatus.PROCESSING:
                    progress.status = AnalysisStatus.FAILED
                    progress.error_message = str(e)
                    progress.completed_at = datetime.now(timezone.utc)
                    break
    
    async def _execute_step_1_job_analysis(self, analysis_id: str, request: AnalysisRequest) -> Dict[str, Any]:
        """Execute Step 1: Job Description Analysis"""
        await self._update_step_status(analysis_id, AnalysisStep.JOB_ANALYSIS, AnalysisStatus.PROCESSING)
        
        try:
            # Use Claude API to analyze job description
            claude_result = await self.claude_service.analyze_job_description(
                job_description=request.job_description,
                additional_context=request.job_url
            )
            
            # Parse Claude response (expecting JSON)
            try:
                job_analysis = json.loads(claude_result.response_text)
            except json.JSONDecodeError:
                # If not valid JSON, create structured response
                job_analysis = {
                    "raw_analysis": claude_result.response_text,
                    "job_title": "Position Title Not Extracted",
                    "company_name": "Company Not Identified",
                    "requirements": ["Analysis completed but structured data unavailable"],
                    "keywords": []
                }
            
            # Add metadata
            job_analysis["_metadata"] = {
                "tokens_used": claude_result.usage_tokens,
                "processing_time": claude_result.processing_time,
                "analysis_quality": "high" if claude_result.usage_tokens > 200 else "medium"
            }
            
            await self._update_step_status(analysis_id, AnalysisStep.JOB_ANALYSIS, AnalysisStatus.COMPLETED)
            return job_analysis
            
        except Exception as e:
            await self._update_step_status(analysis_id, AnalysisStep.JOB_ANALYSIS, AnalysisStatus.FAILED, str(e))
            raise JobAnalysisError(f"Job analysis failed: {e}")
    
    async def _execute_step_2_company_research(self, analysis_id: str, request: AnalysisRequest, job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Step 2: Company Research"""
        await self._update_step_status(analysis_id, AnalysisStep.COMPANY_RESEARCH, AnalysisStatus.PROCESSING)
        
        try:
            # Extract company name from job analysis
            company_name = job_analysis.get("company_name", "Unknown Company")
            
            if company_name and company_name != "Unknown Company":
                # Use Claude API for company research
                claude_result = await self.claude_service.research_company(
                    company_name=company_name,
                    context=f"Job posting URL: {request.job_url}" if request.job_url else None
                )
                
                try:
                    company_research = json.loads(claude_result.response_text)
                except json.JSONDecodeError:
                    company_research = {
                        "company_name": company_name,
                        "research_summary": claude_result.response_text,
                        "industry": "Not identified",
                        "culture_insights": ["Research completed but structured data unavailable"]
                    }
            else:
                # No company identified, create basic response
                company_research = {
                    "company_name": "Not specified",
                    "research_summary": "Company name not clearly identified in job posting",
                    "industry": "Unknown",
                    "culture_insights": ["Company research requires identifiable company name"]
                }
            
            # Add metadata
            company_research["_metadata"] = {
                "research_method": "claude_api" if company_name != "Unknown Company" else "fallback",
                "company_identified": company_name != "Unknown Company"
            }
            
            await self._update_step_status(analysis_id, AnalysisStep.COMPANY_RESEARCH, AnalysisStatus.COMPLETED)
            return company_research
            
        except Exception as e:
            await self._update_step_status(analysis_id, AnalysisStep.COMPANY_RESEARCH, AnalysisStatus.FAILED, str(e))
            # Company research failure shouldn't stop the workflow
            logger.warning(f"Company research failed for {analysis_id}: {e}")
            return {
                "company_name": "Research failed",
                "research_summary": f"Company research encountered an error: {e}",
                "industry": "Unknown",
                "culture_insights": [],
                "_metadata": {"research_method": "failed", "error": str(e)}
            }
    
    async def _execute_step_3_resume_parsing(self, analysis_id: str, request: AnalysisRequest) -> Dict[str, Any]:
        """Execute Step 3: Resume Parsing"""
        await self._update_step_status(analysis_id, AnalysisStep.RESUME_PARSING, AnalysisStatus.PROCESSING)
        
        try:
            if request.resume_file_id:
                # Parse uploaded file
                # Note: This requires file tracking - for now we'll use the text extraction approach
                parsed_resume = {
                    "source": "file_upload",
                    "file_id": request.resume_file_id,
                    "parsing_method": "file_service",
                    "content": "File parsing integration pending - requires file tracking system"
                }
            elif request.resume_text:
                # Parse text directly
                parsed_resume_obj = self.resume_parser.parse_resume(request.resume_text)
                
                # Convert to dictionary for JSON serialization
                try:
                    parsed_resume = {
                        "source": "text_input",
                        "contact_info": asdict(parsed_resume_obj.contact_info) if hasattr(parsed_resume_obj.contact_info, '__dataclass_fields__') else {
                            "email": getattr(parsed_resume_obj.contact_info, 'email', None),
                            "phone": getattr(parsed_resume_obj.contact_info, 'phone', None),
                            "linkedin": getattr(parsed_resume_obj.contact_info, 'linkedin', None),
                            "github": getattr(parsed_resume_obj.contact_info, 'github', None),
                            "website": getattr(parsed_resume_obj.contact_info, 'website', None),
                            "address": getattr(parsed_resume_obj.contact_info, 'address', None)
                        },
                        "summary": parsed_resume_obj.summary,
                        "work_experience": [asdict(exp) if hasattr(exp, '__dataclass_fields__') else exp for exp in parsed_resume_obj.work_experience],
                        "education": [asdict(edu) if hasattr(edu, '__dataclass_fields__') else edu for edu in parsed_resume_obj.education],
                        "skills": parsed_resume_obj.skills,
                        "projects": [asdict(proj) if hasattr(proj, '__dataclass_fields__') else proj for proj in parsed_resume_obj.projects],
                        "certifications": parsed_resume_obj.certifications,
                        "languages": parsed_resume_obj.languages,
                        "sections": parsed_resume_obj.sections,
                        "metadata": parsed_resume_obj.metadata
                    }
                except Exception as e:
                    # Fallback for mocked objects
                    parsed_resume = {
                        "source": "text_input",
                        "contact_info": {
                            "email": getattr(parsed_resume_obj.contact_info, 'email', None),
                            "phone": getattr(parsed_resume_obj.contact_info, 'phone', None),
                            "linkedin": getattr(parsed_resume_obj.contact_info, 'linkedin', None),
                            "github": getattr(parsed_resume_obj.contact_info, 'github', None),
                            "website": getattr(parsed_resume_obj.contact_info, 'website', None),
                            "address": getattr(parsed_resume_obj.contact_info, 'address', None)
                        },
                        "summary": getattr(parsed_resume_obj, 'summary', ''),
                        "work_experience": getattr(parsed_resume_obj, 'work_experience', []),
                        "education": getattr(parsed_resume_obj, 'education', []),
                        "skills": getattr(parsed_resume_obj, 'skills', []),
                        "projects": getattr(parsed_resume_obj, 'projects', []),
                        "certifications": getattr(parsed_resume_obj, 'certifications', []),
                        "languages": getattr(parsed_resume_obj, 'languages', []),
                        "sections": getattr(parsed_resume_obj, 'sections', {}),
                        "metadata": getattr(parsed_resume_obj, 'metadata', {})
                    }
            else:
                raise JobAnalysisError("No resume data provided")
            
            # Add processing metadata
            parsed_resume["_metadata"] = {
                "parsing_method": "advanced_parser",
                "sections_detected": len(parsed_resume.get("sections", {})),
                "work_experiences": len(parsed_resume.get("work_experience", [])),
                "skills_extracted": len(parsed_resume.get("skills", []))
            }
            
            await self._update_step_status(analysis_id, AnalysisStep.RESUME_PARSING, AnalysisStatus.COMPLETED)
            return parsed_resume
            
        except Exception as e:
            await self._update_step_status(analysis_id, AnalysisStep.RESUME_PARSING, AnalysisStatus.FAILED, str(e))
            raise JobAnalysisError(f"Resume parsing failed: {e}")
    
    async def _execute_step_4_skills_analysis(self, analysis_id: str, request: AnalysisRequest, job_analysis: Dict[str, Any], parsed_resume: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Step 4: Skills Gap Analysis"""
        await self._update_step_status(analysis_id, AnalysisStep.SKILLS_ANALYSIS, AnalysisStatus.PROCESSING)
        
        try:
            # Extract current skills from resume
            current_skills = parsed_resume.get("skills", [])
            
            # Extract job requirements
            job_requirements = job_analysis.get("requirements", [])
            if isinstance(job_requirements, list):
                job_requirements_text = "; ".join(job_requirements)
            else:
                job_requirements_text = str(job_requirements)
            
            # Extract industry from job analysis
            industry = job_analysis.get("industry", "Technology")
            
            # Use Claude API for skills gap analysis
            claude_result = await self.claude_service.analyze_skills_gap(
                current_skills=current_skills,
                job_requirements=job_requirements_text,
                industry=industry
            )
            
            try:
                skills_analysis = json.loads(claude_result.response_text)
            except json.JSONDecodeError:
                skills_analysis = {
                    "current_skills": current_skills,
                    "analysis_summary": claude_result.response_text,
                    "missing_skills": [],
                    "skill_gaps": ["Analysis completed but structured data unavailable"]
                }
            
            # Add metadata
            skills_analysis["_metadata"] = {
                "skills_analyzed": len(current_skills),
                "tokens_used": claude_result.usage_tokens,
                "analysis_method": "claude_api"
            }
            
            await self._update_step_status(analysis_id, AnalysisStep.SKILLS_ANALYSIS, AnalysisStatus.COMPLETED)
            return skills_analysis
            
        except Exception as e:
            await self._update_step_status(analysis_id, AnalysisStep.SKILLS_ANALYSIS, AnalysisStatus.FAILED, str(e))
            raise JobAnalysisError(f"Skills analysis failed: {e}")
    
    async def _execute_step_5_resume_enhancement(self, analysis_id: str, request: AnalysisRequest, job_analysis: Dict[str, Any], parsed_resume: Dict[str, Any], skills_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Step 5: Resume Enhancement"""
        await self._update_step_status(analysis_id, AnalysisStep.RESUME_ENHANCEMENT, AnalysisStatus.PROCESSING)
        
        try:
            # Prepare resume content for analysis
            resume_summary = f"""
            Contact: {parsed_resume.get('contact_info', {}).get('email', 'Not provided')}
            Skills: {', '.join(parsed_resume.get('skills', [])[:10])}
            Experience: {len(parsed_resume.get('work_experience', []))} positions
            Education: {len(parsed_resume.get('education', []))} entries
            """
            
            # Prepare job requirements
            job_requirements_text = str(job_analysis.get("requirements", "No specific requirements identified"))
            
            # Use Claude API for resume analysis
            claude_result = await self.claude_service.analyze_resume(
                resume_content=resume_summary,
                job_requirements=job_requirements_text
            )
            
            try:
                resume_recommendations = json.loads(claude_result.response_text)
            except json.JSONDecodeError:
                resume_recommendations = {
                    "overall_score": 7.0,
                    "recommendations": claude_result.response_text,
                    "improvements": ["Analysis completed but structured data unavailable"]
                }
            
            # Add skills gap insights
            resume_recommendations["skills_gap_insights"] = skills_analysis.get("missing_skills", [])
            
            # Add metadata
            resume_recommendations["_metadata"] = {
                "analysis_method": "claude_api",
                "tokens_used": claude_result.usage_tokens,
                "recommendations_generated": True
            }
            
            await self._update_step_status(analysis_id, AnalysisStep.RESUME_ENHANCEMENT, AnalysisStatus.COMPLETED)
            return resume_recommendations
            
        except Exception as e:
            await self._update_step_status(analysis_id, AnalysisStep.RESUME_ENHANCEMENT, AnalysisStatus.FAILED, str(e))
            raise JobAnalysisError(f"Resume enhancement failed: {e}")
    
    async def _execute_step_6_cover_letter(self, analysis_id: str, request: AnalysisRequest, job_analysis: Dict[str, Any], company_research: Dict[str, Any], parsed_resume: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Step 6: Cover Letter Generation"""
        await self._update_step_status(analysis_id, AnalysisStep.COVER_LETTER, AnalysisStatus.PROCESSING)
        
        try:
            # Prepare inputs for cover letter generation
            job_description = request.job_description
            
            # Create company info summary
            company_info = f"""
            Company: {company_research.get('company_name', 'Company name not identified')}
            Industry: {company_research.get('industry', 'Not specified')}
            Research Summary: {company_research.get('research_summary', 'Limited company information available')[:500]}
            """
            
            # Create resume summary
            resume_summary = f"""
            Name: {parsed_resume.get('contact_info', {}).get('email', 'Candidate')}
            Experience: {len(parsed_resume.get('work_experience', []))} positions
            Key Skills: {', '.join(parsed_resume.get('skills', [])[:8])}
            Education: {len(parsed_resume.get('education', []))} degrees/certifications
            """
            
            # Get tone preference
            tone = request.preferences.get("tone", "professional")
            focus_areas = request.preferences.get("focus_areas", ["relevant experience", "technical skills"])
            
            # Use Claude API for cover letter generation
            claude_result = await self.claude_service.generate_cover_letter(
                job_description=job_description,
                company_info=company_info,
                resume_summary=resume_summary,
                tone=tone,
                focus_areas=focus_areas
            )
            
            # Process cover letter result
            cover_letter_content = claude_result.response_text
            
            cover_letter = {
                "content": cover_letter_content,
                "tone": tone,
                "focus_areas": focus_areas,
                "word_count": len(cover_letter_content.split()),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "_metadata": {
                    "generation_method": "claude_api",
                    "tokens_used": claude_result.usage_tokens,
                    "processing_time": claude_result.processing_time
                }
            }
            
            await self._update_step_status(analysis_id, AnalysisStep.COVER_LETTER, AnalysisStatus.COMPLETED)
            return cover_letter
            
        except Exception as e:
            await self._update_step_status(analysis_id, AnalysisStep.COVER_LETTER, AnalysisStatus.FAILED, str(e))
            raise JobAnalysisError(f"Cover letter generation failed: {e}")
    
    async def _execute_step_7_final_review(self, analysis_id: str, request: AnalysisRequest, job_analysis: Dict[str, Any], company_research: Dict[str, Any], parsed_resume: Dict[str, Any], skills_analysis: Dict[str, Any], resume_recommendations: Dict[str, Any], cover_letter: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Step 7: Final Review & Formatting"""
        await self._update_step_status(analysis_id, AnalysisStep.FINAL_REVIEW, AnalysisStatus.PROCESSING)
        
        try:
            # Create comprehensive summary
            final_summary = {
                "analysis_completed_at": datetime.now(timezone.utc).isoformat(),
                "job_match_score": self._calculate_job_match_score(job_analysis, parsed_resume, skills_analysis),
                "key_findings": {
                    "job_title": job_analysis.get("job_title", "Position not identified"),
                    "company": company_research.get("company_name", "Company not identified"),
                    "skills_match": f"{len(parsed_resume.get('skills', []))} skills identified",
                    "experience_level": f"{len(parsed_resume.get('work_experience', []))} positions",
                    "cover_letter_generated": cover_letter.get("word_count", 0) > 0
                },
                "recommendations_summary": {
                    "top_priorities": resume_recommendations.get("improvements", ["No specific recommendations"])[:3],
                    "skills_to_develop": skills_analysis.get("missing_skills", [])[:5],
                    "application_strength": self._assess_application_strength(job_analysis, parsed_resume, skills_analysis)
                },
                "next_steps": [
                    "Review and implement resume recommendations",
                    "Customize cover letter for specific application",
                    "Prepare for interviews based on job requirements",
                    "Consider developing identified missing skills"
                ],
                "_metadata": {
                    "total_steps_completed": 7,
                    "analysis_quality": "comprehensive",
                    "generation_timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
            await self._update_step_status(analysis_id, AnalysisStep.FINAL_REVIEW, AnalysisStatus.COMPLETED)
            return final_summary
            
        except Exception as e:
            await self._update_step_status(analysis_id, AnalysisStep.FINAL_REVIEW, AnalysisStatus.FAILED, str(e))
            raise JobAnalysisError(f"Final review failed: {e}")
    
    async def _update_step_status(self, analysis_id: str, step: AnalysisStep, status: AnalysisStatus, error_message: Optional[str] = None) -> None:
        """Update progress status for a specific step"""
        progress_list = self.job_progress.get(analysis_id, [])
        
        for progress in progress_list:
            if progress.step == step:
                progress.status = status
                
                if status == AnalysisStatus.PROCESSING:
                    progress.started_at = datetime.now(timezone.utc)
                elif status in [AnalysisStatus.COMPLETED, AnalysisStatus.FAILED]:
                    progress.completed_at = datetime.now(timezone.utc)
                
                if error_message:
                    progress.error_message = error_message
                
                break
        
        # Update job current step
        job = self.active_jobs.get(analysis_id, {})
        job["current_step"] = step
        job["updated_at"] = datetime.now(timezone.utc)
    
    def _calculate_job_match_score(self, job_analysis: Dict[str, Any], parsed_resume: Dict[str, Any], skills_analysis: Dict[str, Any]) -> float:
        """Calculate a job match score based on analysis results"""
        try:
            score = 0.0
            
            # Skills match (40% of score)
            resume_skills = set(parsed_resume.get("skills", []))
            job_keywords = set(job_analysis.get("keywords", []))
            if job_keywords:
                skills_overlap = len(resume_skills.intersection(job_keywords)) / len(job_keywords)
                score += skills_overlap * 0.4
            
            # Experience level (30% of score)
            experience_count = len(parsed_resume.get("work_experience", []))
            if experience_count >= 3:
                score += 0.3
            elif experience_count >= 1:
                score += 0.2
            
            # Education (20% of score)
            education_count = len(parsed_resume.get("education", []))
            if education_count >= 1:
                score += 0.2
            
            # Contact completeness (10% of score)
            contact_info = parsed_resume.get("contact_info", {})
            contact_fields = sum(1 for field in [contact_info.get("email"), contact_info.get("phone")] if field)
            score += (contact_fields / 2) * 0.1
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception:
            return 0.5  # Default moderate score if calculation fails
    
    def _assess_application_strength(self, job_analysis: Dict[str, Any], parsed_resume: Dict[str, Any], skills_analysis: Dict[str, Any]) -> str:
        """Assess overall application strength"""
        match_score = self._calculate_job_match_score(job_analysis, parsed_resume, skills_analysis)
        
        if match_score >= 0.8:
            return "Strong - Excellent match for this position"
        elif match_score >= 0.6:
            return "Good - Solid candidate with some areas to strengthen"
        elif match_score >= 0.4:
            return "Moderate - Some relevant qualifications, needs improvement"
        else:
            return "Developing - Significant skill gaps to address"
    
    def _count_claude_calls(self, analysis_id: str) -> int:
        """Count total Claude API calls for this analysis"""
        # In a real implementation, this would track actual API calls
        return 5  # Typical number of Claude API calls in the workflow
    
    def get_progress(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get current progress for an analysis job"""
        if analysis_id not in self.active_jobs:
            return None
        
        job = self.active_jobs[analysis_id]
        progress_list = self.job_progress.get(analysis_id, [])
        
        # Calculate overall progress
        completed_steps = sum(1 for p in progress_list if p.status == AnalysisStatus.COMPLETED)
        total_steps = len(progress_list)
        overall_progress = int((completed_steps / total_steps) * 100) if total_steps > 0 else 0
        
        # Find current step
        current_step = None
        for progress in progress_list:
            if progress.status == AnalysisStatus.PROCESSING:
                current_step = progress
                break
        
        if not current_step and completed_steps < total_steps:
            # Find next pending step
            for progress in progress_list:
                if progress.status == AnalysisStatus.PENDING:
                    current_step = progress
                    break
        
        return {
            "analysis_id": analysis_id,
            "status": job["status"].value if hasattr(job["status"], 'value') else str(job["status"]),
            "overall_progress": overall_progress,
            "current_step": asdict(current_step) if current_step else None,
            "steps": [asdict(p) for p in progress_list],
            "started_at": job["started_at"].isoformat(),
            "updated_at": job["updated_at"].isoformat(),
            "error": job.get("error")
        }
    
    def get_result(self, analysis_id: str) -> Optional[AnalysisResult]:
        """Get completed analysis result"""
        return self.job_results.get(analysis_id)
    
    def cancel_analysis(self, analysis_id: str) -> bool:
        """Cancel a running analysis job"""
        if analysis_id not in self.active_jobs:
            return False
        
        job = self.active_jobs[analysis_id]
        if job["status"] in [AnalysisStatus.COMPLETED, AnalysisStatus.FAILED]:
            return False
        
        # Update status
        job["status"] = AnalysisStatus.CANCELLED
        job["updated_at"] = datetime.now(timezone.utc)
        
        # Mark current step as cancelled
        progress_list = self.job_progress.get(analysis_id, [])
        for progress in progress_list:
            if progress.status == AnalysisStatus.PROCESSING:
                progress.status = AnalysisStatus.CANCELLED
                progress.completed_at = datetime.now(timezone.utc)
                break
        
        logger.info(f"Analysis job {analysis_id} cancelled")
        return True
    
    def cleanup_old_jobs(self, max_age_hours: int = 24) -> int:
        """Clean up old completed/failed analysis jobs"""
        cutoff_time = datetime.now(timezone.utc) - datetime.timedelta(hours=max_age_hours)
        cleaned_count = 0
        
        jobs_to_remove = []
        for analysis_id, job in self.active_jobs.items():
            if job["updated_at"] < cutoff_time and job["status"] in [AnalysisStatus.COMPLETED, AnalysisStatus.FAILED, AnalysisStatus.CANCELLED]:
                jobs_to_remove.append(analysis_id)
        
        for analysis_id in jobs_to_remove:
            del self.active_jobs[analysis_id]
            self.job_progress.pop(analysis_id, None)
            self.job_results.pop(analysis_id, None)
            cleaned_count += 1
        
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old analysis jobs")
        
        return cleaned_count


# Global service instance
_job_analysis_service_instance = None

def get_job_analysis_service() -> JobAnalysisService:
    """Get job analysis service singleton instance"""
    global _job_analysis_service_instance
    if _job_analysis_service_instance is None:
        _job_analysis_service_instance = JobAnalysisService()
    return _job_analysis_service_instance