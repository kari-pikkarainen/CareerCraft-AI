# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CareerCraft AI is an intelligent job application assistant that uses Claude API to analyze job descriptions, research companies, and generate personalized resume recommendations and cover letters.

**IMPORTANT**: This is proprietary software owned by Kari Pikkarainen. All development should respect the proprietary nature of this codebase.

**Current Status:** ✅ **Phase 10 Complete** - Job Analysis Workflow Ready  
**Backend:** Complete (73+ test methods, 6,000+ lines, 58% coverage)  
**Frontend:** Complete 3-step analysis workflow with comprehensive job description form  
**Implementation:** 12,000+ lines of production-ready code (backend + frontend + services)  
**Next Phase:** Real-time progress tracking UI for 7-step workflow

## Architecture

### Tech Stack (Current Implementation)
- **Backend**: ✅ Python 3.9+ with FastAPI (IMPLEMENTED)
- **Frontend**: ✅ React.js with TypeScript (IMPLEMENTED - Phase 9)
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

**Current State**: ✅ **Phase 9 Complete** - API Service Layer with HMAC Authentication

### ✅ Completed Components
- **🔒 Security Framework** - HMAC + JWT authentication, encrypted configuration
- **🛡️ Authentication System** - Session management, rate limiting, token refresh
- **🚀 FastAPI Application** - Production-ready API with health monitoring
- **📊 API Models** - 40+ Pydantic models with comprehensive validation
- **📁 File Upload Service** - Secure PDF/DOCX/TXT processing with validation
- **🔍 Resume Parser** - Intelligent text extraction with structured data parsing
- **🤖 Claude API Integration** - Full Anthropic API client with specialized prompts
- **🚀 Job Analysis Orchestration** - Complete 7-step workflow automation engine
- **⚛️ React Frontend Foundation** - Complete routing, authentication, and UI components
- **🔌 API Service Layer** - HMAC authentication, error handling, service integration
- **🧪 Comprehensive Test Suite** - 73+ test methods with 3,000+ lines of test code

### 🚧 In Development  
- **Phase 10 (Next):** Local development version without authentication barriers
- **Phase 11:** Core job analysis workflow UI components
- **Phase 12:** File upload, progress tracking, and results display
- **Phase 13:** Authentication integration and production features

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

## React Frontend Foundation (IMPLEMENTED - Phase 9)

**Core Implementation:** Complete React TypeScript application with professional UI

**Routing System:** `src/App.tsx` (React Router 6)
- **Protected Routes**: Authentication-based route protection
- **Nested Routing**: Layout wrapper with outlet pattern
- **Route Guards**: Automatic redirect to login for unauthenticated users
- **Navigation**: Active route highlighting and responsive navigation

**Authentication Flow:** `src/contexts/AuthContext.tsx`
- **Context API**: State management with useReducer pattern
- **Session Management**: Token storage and refresh logic (prepared for API)
- **Error Handling**: Comprehensive authentication error states
- **User State**: Email-based user identification and logout functionality

**Layout System:** `src/components/Layout.tsx`
- **Professional Design**: Header, navigation, main content, footer structure
- **Responsive UI**: Mobile-first design with breakpoint optimization
- **Navigation Bar**: Logo, main navigation, user menu with logout
- **Active States**: Visual feedback for current page navigation

**Page Components:** Complete UI implementation
- **LoginPage**: Professional login form with gradient background and validation
- **DashboardPage**: Main dashboard with stats, recent activity, quick actions
- **AnalysisPage**: Placeholder for new analysis workflow (prepared for API)
- **ResultsPage**: Results display layout (prepared for backend integration)
- **HistoryPage**: Analysis history interface (prepared for pagination)
- **ProfilePage**: User profile management (prepared for settings)

**UI Components:** `src/components/`
- **LoadingSpinner**: Configurable loading states (small, medium, large)
- **ErrorBoundary**: Production error handling with detailed error display
- **ProtectedRoute**: Route protection wrapper with loading states

**Styling System:** `src/App.css`
- **CSS Custom Properties**: Comprehensive design system with CSS variables
- **Professional Theme**: Modern color palette with primary/secondary colors
- **Component Library**: Buttons, forms, cards, layouts with consistent styling
- **Responsive Design**: Mobile-optimized with breakpoint-based layouts
- **Dark Mode Ready**: CSS variables prepared for theme switching

**Build System:** Production-ready configuration
- **TypeScript**: Full type safety with strict configuration
- **React 18.2**: Latest React with concurrent features
- **Build Optimization**: 57.39 kB gzipped bundle with tree shaking
- **Development Server**: Hot reload with error overlay

**State Management:** Context API implementation
- **AuthContext**: Authentication state with login/logout actions
- **AnalysisContext**: Job analysis workflow state (prepared for API)
- **Type Safety**: Full TypeScript interfaces for all state

**Integration Points:** Prepared for backend connection
- **API Service Layer**: Placeholder for HMAC authentication (next phase)
- **File Upload**: UI components ready for resume upload integration
- **Progress Tracking**: Layout prepared for real-time progress updates
- **Results Display**: Components ready for job analysis results

**Current Status:**
- ✅ **Complete Routing**: React Router with protected routes
- ✅ **Authentication UI**: Professional login interface with validation
- ✅ **Layout System**: Header, navigation, main content, footer
- ✅ **Dashboard**: Stats, activity, quick actions interface
- ✅ **Component Library**: Loading, error handling, reusable components
- ✅ **Responsive Design**: Mobile-optimized with professional styling
- ✅ **TypeScript Types**: Complete API model interfaces matching backend
- ✅ **API Service Layer**: Complete HMAC authentication with error handling
- ✅ **Local Development Interface**: Complete testing environment with API debugging
- ✅ **Job Description Form**: Comprehensive form with validation and UX features
- ✅ **3-Step Analysis Workflow**: Upload → Job Details → Review & Start

## Development Strategy: Local-First Approach

**Philosophy:** Build core functionality first, add complexity incrementally

**Phase 10: Local Development Version** ✅ COMPLETE
- ✅ Remove authentication barriers for local testing
- ✅ Direct API access with HMAC authentication debugging
- ✅ Complete job analysis workflow implementation
- ✅ End-to-end testing interface without auth complexity

**Phase 11: Progress Tracking & Results** 🚧 NEXT
- Real-time progress tracking UI for 7-step workflow
- Results display components for analysis output
- Cover letter generation interface
- Complete workflow testing and optimization

**Benefits of Local-First Development:**
- **Faster Feedback Loop**: No auth setup required for core feature testing
- **Easier Debugging**: Direct API access with immediate error visibility
- **Core Feature Focus**: Build the main workflow before production features
- **Incremental Complexity**: Add authentication layer after core features work
- **Better Testing**: Full workflow validation without auth dependencies

**Implementation Plan:**
1. ✅ Create local interface bypassing authentication
2. ✅ Build file upload component with drag-and-drop and validation
3. ✅ Implement comprehensive job analysis form with validation
4. ✅ Create 3-step workflow integration (Upload → Form → Review)
5. ✅ Add API testing interface for HMAC authentication debugging
6. 🚧 Build real-time progress tracking for 7-step workflow
7. 🚧 Create results display and workflow completion
8. 📋 Add authentication layer for production use

## API Service Layer Implementation (IMPLEMENTED - Phase 9)

**Complete Service Architecture:** `src/services/` directory

**Core Services:**
- **`apiService.ts`**: HMAC-authenticated API client (500+ lines)
- **`configService.ts`**: Environment configuration management
- **`errorService.ts`**: Centralized error handling and categorization
- **`index.ts`**: Service initialization and health checking

**HMAC Authentication Features:**
- **Signature Generation**: HMAC-SHA256 with Base64 encoding
- **Request Authentication**: X-API-Key, X-Signature, X-Timestamp headers
- **JWT Integration**: Bearer token support for session management
- **FormData Support**: File upload compatibility
- **Error Handling**: Retry logic and structured error processing

**API Coverage:**
- **Authentication**: login, logout, refresh, status endpoints
- **File Management**: upload, download, delete with progress tracking
- **Job Analysis**: complete 7-step workflow automation
- **Health Checks**: service monitoring and validation

**Quality Assurance:**
- TypeScript compilation: ✅ Zero errors
- Production build: ✅ 88.91 kB bundle
- Service initialization with health checks
- Comprehensive error categorization and reporting

## TypeScript Type System (IMPLEMENTED - Phase 9.5)

**Comprehensive Type Coverage:** Complete TypeScript interfaces matching all backend Pydantic models

**Type Organization:** `src/types/` directory structure
- **`enums.ts`**: All enumeration types (`ProcessingStatusEnum`, `FileFormatEnum`, `ToneEnum`)
- **`auth.ts`**: Authentication interfaces (`AuthRequest`, `AuthResponse`, `LoginFormData`, `User`)
- **`files.ts`**: File handling types (`FileInfo`, `FileUploadResponse`, `DroppedFile`)
- **`analysis.ts`**: Job analysis workflow (`JobAnalysisRequest`, `ProgressResponse`, `AnalysisResults`)
- **`api.ts`**: API communication (`ErrorResponse`, `HMACHeaders`, `ApiEndpoints`)
- **`index.ts`**: Main exports and utility types

**Backend Model Mapping:** 100% correspondence with Python Pydantic models
- **Authentication Models**: `AuthRequest`, `AuthResponse`, `SessionInfoResponse`, `StatusResponse`
- **File Upload Models**: `FileInfo`, `FileUploadResponse` with validation constraints
- **Analysis Models**: Complete 7-step workflow types with progress tracking
- **Results Models**: `JobAnalysisResult`, `CompanyResearchResult`, `ResumeAnalysisResult`
- **Error Models**: `ErrorResponse`, `ValidationError` with detailed error handling

**Context Integration:** Updated React contexts to use proper types
- **AuthContext**: Now uses `LoginFormData`, `User`, `AuthState`, `AuthAction` interfaces
- **AnalysisContext**: Full integration with `JobAnalysisRequest`, `ProgressResponse`, `AnalysisResults`
- **Type Safety**: 100% TypeScript compilation with strict mode enabled

**API Readiness:** Types prepared for HMAC authentication implementation
- **Request Signatures**: `HMACHeaders` interface for signed requests
- **Endpoint Constants**: `ApiEndpoints` enum for type-safe URL management
- **Error Handling**: Structured error types with validation details
- **Pagination**: `PaginatedResponse<T>` for list endpoints

**Quality Assurance:**
- **Compilation**: ✅ Zero TypeScript errors (`npm run type-check`)
- **Build**: ✅ Production build successful (57.48 kB bundle)
- **Field Validation**: Exact match with backend constraints and optional fields
- **Enum Consistency**: All enumeration values match backend definitions

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