# CareerCraft AI

An intelligent job application assistant that uses Claude API to analyze job descriptions, research companies, and generate personalized resume recommendations and cover letters.

## 🚀 Implementation Status

**Current Phase:** ✅ **Phase 10 Complete** - Job Analysis Workflow Ready  
**Backend:** Complete (73+ test methods, 6,000+ lines, 58% coverage)  
**Frontend:** Complete 3-step analysis workflow with job description form  
**Next:** Real-time progress tracking and results display

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
- **🔌 API Service Layer** - HMAC authentication, error handling, complete backend integration
- **📋 Job Description Form** - Comprehensive form with validation and user experience features
- **🎯 Complete Analysis Workflow** - 3-step process with file upload and job details
- **🧪 API Testing Interface** - HMAC authentication testing and debugging tools
- **🧪 Comprehensive Test Suite** - 73+ test methods with 3,000+ lines of test code

### 🚧 In Development  
- **Phase 11 (Next):** Real-time progress tracking UI for 7-step workflow
- **Phase 12:** Results display components (analysis, recommendations, cover letter)
- **Phase 13:** End-to-end workflow testing and optimization
- **Phase 14:** Authentication integration and production features

## Features

- **📋 Job Description Analysis**: AI-powered extraction of requirements, skills, and keywords
- **🏢 Company Research**: Automated research for company insights and culture analysis
- **📄 Resume Enhancement**: Intelligent parsing with improvement suggestions and optimization
- **✉️ Cover Letter Generation**: Personalized cover letters based on job and company analysis
- **📊 Real-time Progress Tracking**: 7-step workflow with live progress updates
- **📁 Multi-Format File Support**: Secure processing of PDF, DOCX, and TXT resumes
- **🔒 Enterprise Security**: HMAC signature authentication with encrypted configuration
- **⚡ Production Monitoring**: Comprehensive health checks and Kubernetes-ready probes
- **🤖 Claude AI Integration**: Advanced natural language processing for intelligent analysis

## Tech Stack

- **Backend**: Python 3.9+ with FastAPI (✅ **Implemented**)
- **Frontend**: React.js with TypeScript (🚧 **In Development**)
- **AI Integration**: Anthropic Claude API (✅ **Implemented**)
- **File Processing**: PyPDF2, python-docx, intelligent text extraction (✅ **Implemented**)
- **Database**: SQLite for session storage (✅ **Configured**)
- **Security**: Encrypted configuration, HMAC authentication, JWT sessions (✅ **Implemented**)
- **Testing**: pytest with comprehensive test suite (✅ **Implemented**)

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- Claude API key from Anthropic

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run secure setup script:
```bash
python setup.py
```

5. Configure environment:
```bash
cp .env.template .env
# Edit .env with your settings
```

6. Start the server:
```bash
cd backend
PYTHONPATH=. uvicorn main:app --reload
```

**Backend API will be available at:** `http://localhost:8000`
- **API Documentation:** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`

### Key API Endpoints

**Authentication:**
- `POST /auth/login` - Create session with API credentials
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/logout` - End session

**Job Analysis:**
- `POST /api/v1/analyze-application` - Start 7-step analysis workflow
- `GET /api/v1/analysis/{id}/progress` - Get real-time progress
- `GET /api/v1/analysis/{id}/results` - Get completed results
- `POST /api/v1/analysis/{id}/cancel` - Cancel running analysis

**File Management:**
- `POST /api/v1/files/upload` - Upload resume files (PDF/DOCX/TXT)
- `GET /api/v1/files/{id}` - Download processed files
- `DELETE /api/v1/files/{id}` - Delete uploaded files

### Frontend Setup

The React frontend is in active development with complete routing structure:

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm start
```

**Frontend will be available at:** `http://localhost:3000`

**Local Development Interface:** `http://localhost:3000/local`
- **Development Hub**: Complete testing environment with API status
- **File Upload Test**: `/local/upload` - Test drag-and-drop functionality
- **Job Analysis Workflow**: `/local/analyze` - Complete 3-step process
- **API Connection Test**: `/local/api-test` - HMAC authentication debugging

**Current Status:** 
- ✅ **Local Development Interface**: Complete development hub with API testing
- ✅ **File Upload Component**: Drag-and-drop with validation and progress tracking
- ✅ **Job Description Form**: Comprehensive form with real-time validation
- ✅ **3-Step Analysis Workflow**: Upload → Job Details → Review & Start
- ✅ **API Authentication**: HMAC signature testing and debugging interface
- ✅ **Responsive Design**: Mobile-first UI with accessibility features
- ✅ **TypeScript Integration**: Complete type safety and error handling

## API Authentication

All API requests require authentication headers:
```
X-API-Key: your_api_key
X-Signature: hmac_sha256_signature
X-Timestamp: 2025-07-10T10:30:00Z
```

## Development Approach

### 🏠 Local-First Development Strategy

The project follows a **local-first development approach** to enable rapid testing and iteration:

1. **Phase 1: Local Development Version**
   - Bypass authentication for local testing
   - Direct API access to backend services
   - Focus on core job analysis workflow
   - End-to-end testing without auth barriers

2. **Phase 2: Core Feature Implementation**
   - File upload with drag-and-drop
   - Job description input forms
   - Real-time progress tracking
   - Results display components

3. **Phase 3: Production Integration**
   - Add authentication layer
   - Implement dashboard and history
   - Production security features
   - Deployment optimization

**Benefits:**
- ✅ Faster development cycle
- ✅ Easier debugging and testing
- ✅ Core functionality validation
- ✅ Incremental complexity

### 📝 Environment Setup

The frontend requires API credentials for backend communication. Create a `.env.local` file:

```bash
# Frontend environment configuration
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_API_KEY=your-backend-api-key
REACT_APP_API_SECRET=your-backend-api-secret  
REACT_APP_ENVIRONMENT=development
```

**Note:** The API key and secret are automatically generated during backend setup. You can retrieve them by running the backend and checking the configuration, or use the API test interface to verify connectivity.

### Running Tests

**Comprehensive Test Suite (67/67 tests passing):**

```bash
# Run all tests
PYTHONPATH=backend pytest backend/tests/ -v

# Run specific test suites
PYTHONPATH=backend python backend/tests/test_config.py      # Configuration tests (15 tests)
PYTHONPATH=backend python backend/tests/test_auth.py        # Authentication tests (15 tests)
PYTHONPATH=backend python backend/tests/test_models.py      # API models tests (12 tests)
PYTHONPATH=backend python backend/tests/test_files.py       # File service tests (10 tests)
PYTHONPATH=backend python backend/tests/test_resume_parser.py # Resume parser tests (8 tests)
PYTHONPATH=backend python backend/tests/test_claude.py      # Claude API tests (7 tests)
```

**Test Coverage:**
- **Configuration System:** 15/15 tests ✅
- **Authentication System:** 15/15 tests ✅
- **API Models:** 12/12 tests ✅
- **File Upload Service:** 10/10 tests ✅
- **Resume Parser:** 8/8 tests ✅
- **Claude API Integration:** 7/7 tests ✅
- **Job Analysis Orchestration:** 11/11 tests ✅

### Code Quality

**Backend (Implemented):**
```bash
cd backend
black .                 # Code formatting
flake8 .                # Linting
mypy .                  # Type checking
pytest --cov=.          # Test coverage
```

**Frontend (Implemented):**
```bash
cd frontend
npm run lint            # ESLint
npm run type-check      # TypeScript checking  
npm test                # Jest tests
npm run build           # Production build
```

## Project Structure

```
CareerCraft-AI/
├── backend/                    # ✅ Python FastAPI backend (IMPLEMENTED)
│   ├── main.py                # ✅ FastAPI application entry point
│   ├── config/                # ✅ Encrypted configuration management
│   │   ├── settings.py        #    Configuration loading and validation
│   │   ├── security.py        #    HMAC, JWT, and crypto utilities
│   │   └── __init__.py        #    Package exports
│   ├── api/                   # ✅ API layer (IMPLEMENTED)
│   │   ├── auth.py            #    Authentication endpoints
│   │   ├── files.py           #    File upload endpoints
│   │   ├── analysis.py        #    Job analysis orchestration endpoints
│   │   ├── middleware.py      #    HMAC and JWT middleware
│   │   ├── models.py          #    40+ Pydantic request/response models
│   │   └── __init__.py        #    Package exports
│   ├── services/              # ✅ Business logic (IMPLEMENTED)
│   │   ├── auth_service.py    #    JWT and session management
│   │   ├── file_service.py    #    File upload and processing
│   │   ├── claude_service.py  #    Claude API integration
│   │   ├── job_analysis_service.py # Job analysis orchestration engine
│   │   └── __init__.py        #    Package exports
│   ├── utils/                 # ✅ Utility modules (IMPLEMENTED)
│   │   ├── parsers.py         #    Resume parsing and text extraction
│   │   └── __init__.py        #    Package exports
│   ├── tests/                 # ✅ Comprehensive test suite (IMPLEMENTED)
│   │   ├── test_config.py     #    15 configuration tests
│   │   ├── test_auth.py       #    15 authentication tests
│   │   ├── test_models.py     #    12 API model tests
│   │   ├── test_files.py      #    10 file service tests
│   │   ├── test_resume_parser.py #  8 resume parser tests
│   │   ├── test_claude.py     #    7 Claude API tests
│   │   ├── test_job_analysis.py # 11 job analysis tests
│   │   └── test_fastapi.py    #    3 integration tests
│   ├── setup.py               # ✅ Secure configuration setup
│   ├── requirements.txt       # ✅ Python dependencies
│   └── logs/                  # ✅ Application logs
├── frontend/                  # ✅ React TypeScript frontend (IMPLEMENTED)
│   ├── package.json           # ✅ Dependencies and build configuration
│   ├── tsconfig.json          # ✅ TypeScript configuration
│   ├── public/                # ✅ Static assets and HTML template
│   │   ├── index.html         #    Main HTML template
│   │   └── manifest.json      #    PWA manifest
│   └── src/                   # ✅ Complete React application
│       ├── App.tsx            #    Main app with routing
│       ├── App.css            #    Global styles and CSS variables
│       ├── index.tsx          #    Application entry point
│       ├── components/        # ✅ Complete UI component library
│       │   ├── Layout.tsx     #    Main layout with navigation
│       │   ├── ProtectedRoute.tsx # Route protection
│       │   ├── LoadingSpinner.tsx # Loading states
│       │   ├── ErrorBoundary.tsx  # Error handling
│       │   ├── FileUpload.tsx #    Drag-and-drop file upload with validation
│       │   └── JobDescriptionForm.tsx # Comprehensive form with validation
│       ├── contexts/          # ✅ State management
│       │   ├── AuthContext.tsx #   Authentication state
│       │   └── AnalysisContext.tsx # Analysis workflow state
│       ├── pages/             # ✅ Complete page implementation
│       │   ├── LoginPage.tsx  #    Authentication page
│       │   ├── DashboardPage.tsx # Main dashboard
│       │   ├── AnalysisPage.tsx # Complete 3-step analysis workflow
│       │   ├── ResultsPage.tsx #  Results display (placeholder)
│       │   ├── HistoryPage.tsx #  Analysis history (placeholder)
│       │   ├── LocalDevelopmentPage.tsx # Development hub with tools
│       │   ├── LocalFileUploadPage.tsx  # File upload testing
│       │   └── ApiTestPage.tsx #    API authentication testing
│       ├── services/          # ✅ Complete API service layer
│       │   ├── index.ts       #    Service initialization and exports
│       │   ├── apiService.ts  #    HMAC-authenticated API client
│       │   ├── configService.ts #  Environment configuration management
│       │   └── errorService.ts #   Centralized error handling
│       ├── types/             # ✅ Complete TypeScript type definitions
│       │   ├── index.ts       #    Main exports and utility types
│       │   ├── enums.ts       #    All enumeration types
│       │   ├── auth.ts        #    Authentication interfaces
│       │   ├── files.ts       #    File handling types
│       │   ├── analysis.ts    #    Job analysis workflow types
│       │   └── api.ts         #    API communication interfaces
│       └── utils/             # 🚧 Utility functions (planned)
├── LICENSE                    # ✅ Proprietary software license
├── COPYRIGHT                  # ✅ Copyright notice
├── README.md                  # ✅ Updated documentation  
├── CLAUDE.md                  # ✅ Development guidance
└── job_agent_spec.md         # ✅ Technical specification
```

**Legend:** ✅ Implemented | 🚧 Planned | ⚠️ Issues

## Security

- All sensitive configuration is encrypted using Fernet symmetric encryption
- API requests use HMAC-SHA256 signatures for integrity verification
- File uploads are validated for size, format, and security
- Session management uses JWT tokens with configurable expiration

## Workflow

1. **Job Description Analysis** (14%) - Extract requirements and metadata
2. **Company Research** (28%) - Gather company insights and culture
3. **Resume Parsing** (42%) - Extract and structure resume content
4. **Skills Gap Analysis** (57%) - Compare resume vs job requirements
5. **Resume Enhancement** (71%) - Generate improvement suggestions
6. **Cover Letter Generation** (85%) - Create personalized cover letters
7. **Final Review** (100%) - Quality check and formatting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is proprietary software owned by Kari Pikkarainen. All rights reserved.
See the LICENSE file for full terms and conditions.

## Support

For issues and questions, please open an issue in the GitHub repository.