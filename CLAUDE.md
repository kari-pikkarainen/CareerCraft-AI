# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CareerCraft AI is an intelligent job application assistant that uses Claude API to analyze job descriptions, research companies, and generate personalized resume recommendations and cover letters.

**Current Status:** ✅ **Phase 8 Complete** - Job Analysis Orchestration Engine  
**Test Coverage:** 58% overall (73+ test methods, with core components 79-93%)  
**Implementation:** 6,000+ lines of production-ready backend code

## Architecture

### Tech Stack (Current Implementation)
- **Backend**: ✅ Python 3.9+ with FastAPI (IMPLEMENTED)
- **Frontend**: 🚧 React.js with TypeScript (PLANNED)
- **AI Integration**: ✅ Anthropic Claude API (IMPLEMENTED)
- **File Processing**: ✅ PDF/DOCX/TXT parsing with intelligent extraction (IMPLEMENTED)
- **Job Orchestration**: ✅ 7-step workflow automation engine (IMPLEMENTED)
- **Database**: ✅ SQLite for session storage (CONFIGURED)
- **Security**: ✅ Complete authentication system (IMPLEMENTED)
- **Testing**: ✅ pytest with 73+ test methods (IMPLEMENTED)

### Security Architecture (IMPLEMENTED)
- ✅ HMAC-based API authentication with JWT session management
- ✅ Encrypted configuration storage using Fernet encryption
- ✅ Interactive setup script (`setup.py`) for secure credential initialization
- ✅ Rate limiting (60 requests/minute per API key)
- ✅ Session management with automatic cleanup
- ✅ Request signing with `X-API-Key`, `X-Signature`, `X-Timestamp` headers

## Core Workflow (IMPLEMENTED)

The system implements a complete 7-step processing pipeline with orchestration engine:
1. **Job Description Analysis (14%)** - Claude API extracts requirements, keywords, and metadata
2. **Company Research (28%)** - Claude API researches company culture and insights  
3. **Resume Parsing (42%)** - Advanced parser extracts structured data from PDF/DOCX/TXT
4. **Skills Gap Analysis (57%)** - Claude API compares resume vs job requirements
5. **Resume Enhancement (71%)** - Claude API generates improvement recommendations
6. **Cover Letter Generation (85%)** - Claude API creates personalized cover letters
7. **Final Review & Formatting (100%)** - Quality check, scoring, and final summary

**Features:**
- ✅ Real-time progress tracking with percentage completion
- ✅ Job match scoring algorithm (skills, experience, education, contact completeness)
- ✅ Error handling and graceful degradation
- ✅ Job cancellation and cleanup mechanisms
- ✅ In-memory job storage with automatic cleanup after 24 hours
- ✅ Comprehensive logging and monitoring

## Key API Endpoints (IMPLEMENTED)

**Authentication:**
- `POST /auth/login` - Create session with API credentials  
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/logout` - End session

**Job Analysis (NEW):**
- `POST /api/v1/analyze-application` - Start 7-step analysis workflow
- `GET /api/v1/analysis/{analysis_id}/progress` - Real-time progress tracking  
- `GET /api/v1/analysis/{analysis_id}/results` - Retrieve completed analysis
- `POST /api/v1/analysis/{analysis_id}/cancel` - Cancel running analysis
- `GET /api/v1/analysis/history` - Analysis history with pagination
- `POST /api/v1/analysis/cleanup` - Admin cleanup of old jobs
- `GET /api/v1/analysis/health` - Service health monitoring

**File Management:**
- `POST /api/v1/files/upload` - Upload resume files (PDF/DOCX/TXT)
- `GET /api/v1/files/{file_id}` - Download processed files
- `DELETE /api/v1/files/{file_id}` - Delete uploaded files

## Implementation Status

**Current State**: ✅ **Phase 8 Complete** - Job Analysis Orchestration Engine

### ✅ Completed Components
- **🔒 Security Framework** - HMAC + JWT authentication, encrypted configuration
- **🛡️ Authentication System** - Session management, rate limiting, token refresh
- **🚀 FastAPI Application** - Production-ready API with health monitoring
- **📊 API Models** - 40+ Pydantic models with comprehensive validation
- **📁 File Upload Service** - Secure PDF/DOCX/TXT processing with validation
- **🔍 Resume Parser** - Intelligent text extraction with structured data parsing
- **🤖 Claude API Integration** - Full Anthropic API client with specialized prompts
- **🚀 Job Analysis Orchestration** - Complete 7-step workflow automation engine
- **🧪 Comprehensive Test Suite** - 73+ test methods with 3,000+ lines of test code

### 🚧 In Development
- **Phase 9:** Company research automation service
- **Phase 10:** Resume enhancement recommendations engine
- **Phase 11:** Real-time progress updates via WebSocket

### 📊 Test Coverage

**Overall Coverage: 58%** (1,718 uncovered lines out of 4,070 total)

**High Coverage Components (80%+):**
- **Resume Parser (utils/parsers.py):** 93% coverage ✅
- **Configuration System:** 87% coverage (15 tests) ✅  
- **Job Analysis Orchestration:** 79% coverage (11 tests) ✅
- **Authentication System:** 81% coverage (15 tests) ✅
- **API Models:** 83% coverage (12 tests) ✅

**Medium Coverage Components (50-79%):**
- **Claude API Integration:** 60% coverage (7 tests) ⚠️
- **Resume Parser Tests:** 54% coverage ⚠️
- **FastAPI Integration:** 52% coverage ⚠️

**Low Coverage Components (Below 50%):**
- **File Upload Service:** 22% coverage (10 tests) ❌ 
- **Claude Service Tests:** 34% coverage ❌
- **File Service Tests:** 26% coverage ❌

**Improvement Priorities:**
1. File service testing (22% → 80%+)
2. Claude service test fixes and coverage improvement
3. Integration test configuration issues
4. Edge case and error scenario testing

## Development Phases

The specification outlines 20 implementation phases:
- **Phases 1-5**: Foundation & Security (setup, config, auth)
- **Phases 6-10**: Core Processing Engine (file upload, Claude API, analysis)
- **Phases 11-15**: User Interface & Workflow (React frontend, progress tracking)
- **Phases 16-20**: Production & Polish (testing, optimization, deployment)

## Security Requirements

- **Never commit sensitive data**: All credentials stored encrypted via setup script
- **Authentication required**: All API endpoints require HMAC signature verification
- **File validation**: Resume uploads must be validated for size, format, and security
- **Rate limiting**: Implement request throttling to prevent abuse

## File Processing (IMPLEMENTED)

- **Supported formats**: PDF (PyPDF2), DOCX (python-docx), TXT with fallback MIME detection
- **Size limits**: Maximum 10MB file uploads with configurable limits
- **Security scanning**: Malicious content detection, file structure validation
- **Intelligent parsing**: Resume section detection, contact extraction, technology identification
- **Temporary storage**: Secure temp files with automatic cleanup after 24 hours
- **Structured extraction**: Work experience, education, skills, projects, certifications

## Job Analysis Orchestration Engine (IMPLEMENTED)

**Core Service:** `services/job_analysis_service.py` (850+ lines)
- **7-step workflow automation**: Complete pipeline from job analysis to final review
- **Real-time progress tracking**: Percentage completion with step-by-step status
- **Job match scoring**: Algorithm evaluating skills overlap, experience level, education, contact completeness
- **Error handling**: Graceful degradation with comprehensive error management
- **Session management**: Long-running job tracking with proper cleanup
- **In-memory storage**: Job storage with automatic cleanup after 24 hours
- **Cancellation support**: Users can cancel running analyses
- **Singleton pattern**: Single service instance with proper resource management

**API Endpoints:** `api/analysis.py` (300+ lines)
- **Main workflow endpoint**: `/api/v1/analyze-application` with form data support
- **Progress monitoring**: Real-time status updates via `/api/v1/analysis/{id}/progress`
- **Results retrieval**: Complete analysis results via `/api/v1/analysis/{id}/results`
- **Job management**: Cancellation, history, cleanup, and health monitoring
- **Authentication**: Full JWT integration with session validation
- **Input validation**: Comprehensive form validation and error handling

**Test Coverage:** `tests/test_job_analysis.py` (400+ lines, 79% coverage)
- **Unit tests**: Service initialization, step configuration, progress tracking
- **Workflow tests**: Complete 7-step execution with mocked dependencies
- **Integration tests**: End-to-end workflow validation
- **Edge cases**: Cancellation, cleanup, error scenarios

## Claude API Integration (IMPLEMENTED)

- **Full async client**: Anthropic Claude API with streaming support
- **Specialized prompts**: 5 prompt templates for different analysis types
- **Rate limiting**: 50 requests/minute, 40k tokens/minute with automatic tracking
- **Error handling**: Comprehensive error handling with custom exceptions
- **Usage monitoring**: Real-time token and request usage statistics
- **Prompt types**: Job analysis, company research, resume analysis, cover letter generation, skills gap analysis
- **Orchestration integration**: Full integration with job analysis workflow

## Testing Strategy

**Current Status**: 73+ test methods, 58% overall coverage, 3,000+ lines of test code

**Test Types Implemented:**
- **Unit tests**: Individual functions, security components, service initialization
- **Integration tests**: API endpoints, Claude API integration, database operations
- **Workflow tests**: Complete 7-step job analysis pipeline with mocked dependencies
- **Security tests**: Authentication, HMAC signatures, JWT validation, file upload security
- **Coverage tests**: Automated coverage reporting with detailed metrics

**Test Infrastructure:**
- **pytest framework**: Async test support, fixtures, parametrized tests
- **Mocking strategy**: Comprehensive mocking of external dependencies (Claude API, file system)
- **Test data**: Realistic job descriptions, resumes, and API responses
- **CI/CD ready**: All tests can be run in CI environments

**Coverage Targets (Improvement Plan):**
- **High Priority**: File service (22% → 80%+), Claude service (60% → 80%+)
- **Medium Priority**: Integration tests, error scenario coverage
- **Performance tests**: File processing times, concurrent user handling (planned)

## Performance Requirements

- File upload: < 30 seconds for 10MB files
- Job analysis: < 2 minutes per application
- Concurrent users: Support 10+ simultaneous sessions
- API response time: < 500ms for status checks

## Development Notes

- Follow test-driven development methodology
- Implement security-first approach with encrypted config from start
- Use progress tracking service for real-time user feedback
- Claude API integration requires structured prompt templates
- Company research service needs respectful web scraping with rate limiting