# CareerCraft AI - Technical Specification

## 1. Project Overview

### 1.1 Purpose
Build CareerCraft AI, an intelligent job application agent that analyzes job descriptions, researches companies, and generates personalized resume recommendations and cover letters using Claude LLM API.

### 1.2 Technology Stack
- **Backend**: Python 3.9+, FastAPI
- **Frontend**: React.js with TypeScript
- **AI Integration**: Anthropic Claude API
- **File Processing**: PyPDF2, python-docx
- **Web Research**: Beautiful Soup, requests
- **Database**: SQLite (for storing application history)
- **Deployment**: Docker containers

## 2. System Architecture

### 2.1 Backend Components
```
/backend
├── main.py                    # FastAPI application entry point
├── setup.py                   # Initial setup script for secure configuration
├── config/
│   ├── settings.py           # Configuration management
│   ├── security.py           # Security utilities
│   └── database.py           # Database configuration
├── agents/
│   ├── job_agent.py          # Main agent orchestrator
│   ├── analyzers/
│   │   ├── job_analyzer.py          # Job description analysis
│   │   ├── resume_analyzer.py       # Resume parsing and analysis
│   │   └── company_researcher.py    # Company research
│   └── generators/
│       ├── resume_enhancer.py       # Resume improvement suggestions
│       └── cover_letter_generator.py # Cover letter creation
├── api/
│   ├── routes.py             # API endpoints
│   ├── models.py             # Pydantic models
│   ├── auth.py               # Authentication middleware
│   └── middleware.py         # Request/response middleware
├── services/
│   ├── claude_service.py     # Claude API integration
│   ├── file_service.py       # File upload/processing
│   ├── research_service.py   # Web research utilities
│   └── auth_service.py       # Authentication service
├── utils/
│   ├── parsers.py            # Resume parsing utilities
│   ├── validators.py         # Input validation
│   └── crypto.py             # Encryption utilities
├── tests/
│   ├── test_agents/          # Agent tests
│   ├── test_api/             # API endpoint tests
│   ├── test_services/        # Service layer tests
│   ├── test_utils/           # Utility tests
│   ├── conftest.py           # Test configuration
│   └── fixtures/             # Test data fixtures
└── requirements.txt
```

### 2.2 Frontend Components
```
/frontend
├── src/
│   ├── components/
│   │   ├── FileUpload.tsx           # Resume upload component
│   │   ├── JobDescriptionInput.tsx  # Job description input
│   │   ├── ProgressTracker.tsx      # Progress indicator
│   │   ├── ResultsDisplay.tsx       # Results presentation
│   │   └── CompanyInsights.tsx      # Company research display
│   ├── pages/
│   │   ├── Home.tsx                 # Main application page
│   │   └── History.tsx              # Application history
│   ├── services/
│   │   ├── api.ts                   # API service layer
│   │   └── auth.ts                  # Authentication service
│   ├── types/
│   │   └── index.ts                 # TypeScript type definitions
│   ├── utils/
│   │   ├── helpers.ts               # Utility functions
│   │   └── crypto.ts                # Client-side crypto utilities
│   └── __tests__/                   # Frontend tests
│       ├── components/              # Component tests
│       ├── services/                # Service tests
│       └── utils/                   # Utility tests
├── public/
├── package.json
├── tsconfig.json
└── jest.config.js                   # Test configuration
```

## 3. Security & Authentication

### 3.1 Setup Script
A secure setup script that service hosters run before deployment:

**Purpose**: Initialize CareerCraft AI with encrypted configuration storage

**Features**:
- Interactive configuration collection (Claude API key, database settings, security parameters)
- Automatic encryption key generation with proper file permissions
- Encrypted storage of all sensitive configuration data
- API key/secret pair generation for frontend-backend communication
- Database initialization with secure access controls

**Configuration Items**:
- Claude API credentials
- Database connection settings
- JWT secrets and session timeouts
- Rate limiting parameters
- File processing limits
- Security policies

### 3.2 Configuration Management
**Secure Configuration Service**:
- Encrypted storage using Fernet symmetric encryption
- Runtime decryption of configuration values
- Environment-specific configuration support
- Automatic key rotation capabilities
- Audit logging for configuration access

**Configuration Properties**:
- `claude_api_key`: Encrypted Claude API access
- `database_url`: Database connection string
- `jwt_secret`: JWT token signing key
- `api_key/api_secret`: Frontend-backend authentication
- `session_timeout`: User session duration
- `max_file_size`: File upload limits

### 3.3 Authentication Service
**HMAC-based Request Authentication**:
- API key identification with secret-based signing
- Timestamp validation to prevent replay attacks
- Request body integrity verification
- Configurable signature algorithms (SHA256 default)

**JWT Session Management**:
- Stateless session tokens with configurable expiration
- Role-based access control support
- Automatic token refresh mechanisms
- Secure token storage recommendations

### 3.4 Authentication Middleware
**Request Processing Pipeline**:
- Header validation (API key, signature, timestamp)
- Signature verification using HMAC
- JWT token extraction and verification
- Rate limiting enforcement
- Request/response logging for security auditing

## 4. API Specification

### 4.1 Authentication Headers
All API requests must include:
```
X-API-Key: your_api_key
X-Signature: hmac_sha256_signature
X-Timestamp: 2025-07-10T10:30:00Z
Authorization: Bearer jwt_token (for authenticated endpoints)
```

### 4.2 Core Endpoints

#### POST /api/v1/analyze-application
**Purpose**: Process job application and generate recommendations

**Request Body**:
- `job_description`: string - Job posting text
- `job_url`: string (optional) - URL to job posting
- `resume_file`: file (PDF/DOCX) - User's resume
- `preferences`: object - User preferences for tone and focus areas

**Response**:
- `session_id`: uuid - Unique session identifier
- `status`: string - Processing status (processing|completed|failed)
- `progress`: object - Current progress information

#### GET /api/v1/status/{session_id}
**Purpose**: Check processing status and get progress updates

**Response**:
- `session_id`: uuid - Session identifier
- `status`: string - Current processing status
- `progress`: object - Detailed progress information with percentage and ETA
- `error_message`: string (if failed) - Error details

#### GET /api/v1/results/{session_id}
**Purpose**: Retrieve completed analysis results

**Response**:
- `job_analysis`: object - Extracted job requirements and metadata
- `company_research`: object - Company insights and culture information
- `resume_recommendations`: object - Improvement suggestions and scoring
- `cover_letter`: object - Generated cover letter with key points

### 4.3 Supporting Endpoints

#### GET /api/v1/history
**Purpose**: Get user's application history

#### DELETE /api/v1/session/{session_id}
**Purpose**: Clean up session data

## 5. Processing Workflow

### 5.1 Seven-Step Process

1. **Step 1: Job Description Analysis** (14%)
   - Extract job title, company, requirements
   - Identify key skills and qualifications
   - Determine experience level and role type

2. **Step 2: Company Research** (28%)
   - Search company website and about page
   - Find recent news and press releases
   - Identify company culture and values
   - Gather industry context

3. **Step 3: Resume Parsing** (42%)
   - Extract text from PDF/DOCX
   - Parse sections (experience, skills, education)
   - Identify current keywords and achievements

4. **Step 4: Skills Gap Analysis** (57%)
   - Compare resume skills vs job requirements
   - Identify missing keywords
   - Assess experience relevance

5. **Step 5: Resume Enhancement** (71%)
   - Generate specific improvement suggestions
   - Recommend keyword additions
   - Suggest formatting improvements

6. **Step 6: Cover Letter Generation** (85%)
   - Create personalized cover letter
   - Incorporate company research
   - Align with job requirements

7. **Step 7: Final Review & Formatting** (100%)
   - Quality check all outputs
   - Format results for presentation
   - Generate summary insights

### 5.2 Progress Tracking Implementation

**Progress Tracking Service**:
- Session-based progress storage (Redis/in-memory)
- Real-time updates via WebSocket or polling
- Granular step tracking with percentage completion
- Estimated time remaining calculations
- Error state handling and recovery

**Progress Data Structure**:
- Current step number and description
- Overall percentage completion
- Step-specific progress details
- Time estimates and elapsed time
- Error messages and retry information

## 6. Frontend User Interface

### 6.1 Main Application Flow

1. **Upload Screen**
   - File upload area for resume (drag & drop)
   - Job description text area or URL input
   - Preferences selection (tone, focus areas)
   - Submit button

2. **Progress Screen**
   - Multi-step progress bar
   - Current step indicator with animation
   - Estimated time remaining
   - Cancel option

3. **Results Screen**
   - Tabbed interface:
     - Resume Recommendations
     - Cover Letter
     - Company Insights
     - Application Strategy
   - Download options (PDF, DOCX)
   - Save to history option

### 6.2 Progress Indicator Component

**Component Design**:
- Animated progress bar with smooth transitions
- Step indicators with visual feedback
- Estimated time display with dynamic updates
- Error state visualization
- Responsive design for mobile and desktop

**Props Interface**:
- `currentStep`: number - Current processing step
- `totalSteps`: number - Total number of steps
- `stepName`: string - Current step description
- `percentage`: number - Overall completion percentage
- `estimatedTime?`: string - Estimated time remaining
- `error?`: string - Error message if processing failed

**State Management**:
- Real-time updates via API polling or WebSocket
- Optimistic UI updates for better user experience
- Error handling with retry mechanisms
- Progress persistence across page refreshes

### 6.3 Frontend Authentication Service

**Authentication Service Design**:
- HMAC signature generation for API requests
- Automatic header injection for authenticated requests
- Token management and refresh handling
- Secure credential storage recommendations

**Service Interface**:
- `getAuthHeaders(body: string)`: Generate authentication headers
- `authenticatedRequest(url, method, body?)`: Make authenticated API calls
- `refreshToken()`: Handle token refresh logic
- `logout()`: Clear authentication state

**Security Features**:
- Automatic timestamp generation for requests
- HMAC-SHA256 signature computation
- Request body integrity verification
- Secure storage of API credentials

## 7. Claude API Integration

### 7.1 Service Implementation

**Claude Service Architecture**:
- Centralized Claude API client management
- Prompt template system for consistent AI interactions
- Response parsing and validation
- Error handling and retry logic
- Rate limiting and usage tracking

**Service Methods**:
- `analyze_job_description(job_text)`: Extract job requirements and metadata
- `research_company(company_name, context)`: Gather company insights
- `enhance_resume(resume_data, job_analysis)`: Generate improvement recommendations
- `generate_cover_letter(context)`: Create personalized cover letters

**Prompt Engineering**:
- Structured prompts for consistent outputs
- Context injection for personalized responses
- Output format specifications (JSON schemas)
- Few-shot examples for improved accuracy

### 7.2 Prompt Templates

**Template Categories**:
- Job analysis prompt templates
- Company research prompt templates  
- Resume enhancement prompt templates
- Cover letter generation prompt templates

**Template Features**:
- Variable substitution for dynamic content
- Structured output requirements
- Context preservation across interactions
- Quality assurance guidelines

## 8. File Processing Requirements

### 8.1 Supported Formats
- PDF (using PyPDF2)
- DOCX (using python-docx)
- TXT (plain text)

### 8.2 Resume Parser

**Parser Architecture**:
- Multi-format support (PDF, DOCX, TXT)
- Content extraction with structure preservation
- Section identification and classification
- Metadata extraction (contact info, skills, experience)

**Parsing Capabilities**:
- Text extraction from various file formats
- Section detection (experience, education, skills, etc.)
- Contact information identification
- Skills and keyword extraction
- Experience timeline parsing
- Education and certification detection

## 9. Error Handling & Validation

### 9.1 Input Validation
- File size limits (max 10MB)
- File format validation
- Job description length limits
- Required field validation

### 9.2 Error Responses
**Error Response Format**:
- `error`: boolean - Error flag
- `message`: string - Human-readable error message
- `error_code`: string - Machine-readable error code
- `details`: object - Additional error context

**Common Error Codes**:
- `FILE_TOO_LARGE`: File exceeds size limit
- `INVALID_FORMAT`: Unsupported file format
- `MISSING_REQUIRED_FIELD`: Required input missing
- `PROCESSING_ERROR`: Internal processing failure
- `RATE_LIMIT_EXCEEDED`: Too many requests

## 10. Security & Privacy

### 10.1 Data Handling
- Temporary file storage (auto-delete after processing)
- No permanent storage of resume content
- Session-based data management
- Secure file upload validation

### 10.2 API Security
- Rate limiting
- Input sanitization
- CORS configuration
- Request signing with HMAC
- Encrypted credential storage

## 11. Test-Driven Development

### 11.1 Testing Strategy
- **Unit Tests**: Test individual functions and classes in isolation
- **Integration Tests**: Test component interactions and data flow
- **End-to-End Tests**: Test complete user workflows and scenarios
- **Security Tests**: Test authentication, authorization, and data protection
- **Performance Tests**: Test system behavior under load conditions

### 11.2 Test Categories

**Unit Testing Focus Areas**:
- Authentication service validation logic
- Resume parsing accuracy and edge cases
- Job analysis extraction algorithms
- Configuration management security
- File processing error handling

**Integration Testing Scenarios**:
- API endpoint request/response cycles
- Database operations and data persistence
- Claude API integration and error handling
- File upload and processing workflows
- Progress tracking and state management

**End-to-End Testing Workflows**:
- Complete job application analysis journey
- User authentication and session management
- File upload, processing, and result retrieval
- Error recovery and retry mechanisms
- Multi-user concurrent access scenarios

**Security Testing Requirements**:
- Authentication bypass attempts
- Input validation and sanitization
- File upload security (malicious files)
- API rate limiting enforcement
- Configuration data encryption verification

**Performance Testing Metrics**:
- File upload and processing times
- Concurrent user handling capacity
- API response time benchmarks
- Memory usage under load
- Database query optimization

### 11.3 Test Data Requirements

**Sample Job Descriptions**:
- Various industries and role levels
- Different formats and structures
- Edge cases (minimal/excessive information)
- Multiple languages (if supported)

**Test Resume Files**:
- Different file formats (PDF, DOCX, TXT)
- Various resume styles and layouts
- Different experience levels and backgrounds
- Edge cases (corrupted files, large files)

**Mock Company Data**:
- Public companies with available information
- Startups with limited online presence
- Non-English company information
- Companies with recent news/changes

### 11.4 Test Environment Setup

**Isolated Testing Environment**:
- Separate test database instances
- Mock external API services
- Controlled file system access
- Isolated configuration management

**Test Data Management**:
- Automated test data generation
- Test data cleanup procedures
- Consistent test state initialization
- Data privacy compliance in testing

### 11.5 Continuous Integration Requirements

**Automated Testing Pipeline**:
- Unit tests on every commit
- Integration tests on pull requests
- End-to-end tests on deployment candidates
- Security scans and vulnerability checks
- Performance benchmarking on releases

**Test Coverage Requirements**:
- Minimum 80% code coverage for critical paths
- 100% coverage for security-related functions
- API endpoint coverage verification
- Error handling path validation

### 11.6 Test Documentation

**Test Case Specifications**:
- Test objective and expected outcomes
- Input data requirements and setup
- Success criteria and failure conditions
- Performance benchmarks and thresholds

**Testing Guidelines**:
- Test naming conventions
- Mock service usage patterns
- Test data creation standards
- Error condition simulation methods

## 12. Performance Requirements

- File upload: < 30 seconds for 10MB files
- Job analysis: < 2 minutes per application
- Concurrent users: Support 10+ simultaneous sessions
- Response time: < 500ms for status checks

## 13. Deployment Specification

### 13.1 Docker Configuration

**Backend Dockerfile Requirements**:
- Python 3.9-slim base image
- Application dependencies installation
- Working directory setup
- Uvicorn server configuration

**Frontend Dockerfile Requirements**:
- Node.js base image for build process
- Nginx for production serving
- Multi-stage build optimization
- Static asset optimization

### 13.2 Environment Variables
**Required Environment Variables**:
- `CLAUDE_API_KEY`: Claude API access key
- `FRONTEND_URL`: Frontend application URL
- `MAX_FILE_SIZE`: Maximum file upload size
- `SESSION_TIMEOUT`: Session expiration time

### 13.3 Setup Instructions

**Initial Setup Process**:
1. **Repository Setup**: Clone repository and navigate to project directory
2. **Secure Configuration**: Run setup script to configure encrypted settings
3. **Environment Preparation**: Install dependencies and configure environment variables
4. **Service Deployment**: Deploy backend and frontend services using Docker
5. **Health Verification**: Verify all services are running and communicating properly

**Backend Deployment Steps**:
- Docker image building with production optimizations
- Container deployment with volume mounting for persistent data
- Environment variable injection for runtime configuration
- Health check endpoint verification

**Frontend Deployment Steps**:
- Dependency installation and build process
- Production build optimization
- Static asset serving configuration
- API endpoint configuration for backend communication

**Production Deployment Considerations**:
- Container orchestration with docker-compose
- Load balancing and scaling strategies
- SSL/TLS certificate configuration
- Database backup and recovery procedures
- Monitoring and logging setup

## 14. Future Enhancements

- Multiple resume format support
- Batch processing for multiple jobs
- Resume template generation
- Interview preparation suggestions
- Application tracking integration
- Mobile application support
- Advanced analytics and reporting
- Integration with job boards (LinkedIn, Indeed)
- AI-powered salary negotiation guidance
- Skills gap analysis with learning recommendations

## 15. Development Workflow

### 15.1 Test-Driven Development Process
**TDD Cycle Implementation**:
- **Red Phase**: Write failing tests that define desired functionality
- **Green Phase**: Implement minimal code to make tests pass
- **Refactor Phase**: Improve code quality while maintaining test coverage
- **Iteration**: Repeat cycle for each feature and component

**TDD Best Practices**:
- Write tests before implementation code
- Keep tests simple and focused on single behaviors
- Use descriptive test names that explain expected behavior
- Maintain high test coverage (>80% for critical paths)
- Regular refactoring to improve code quality

### 15.2 Git Workflow Strategy
**Branch Management**:
- Feature branches for new functionality development
- Pull request reviews for code quality assurance
- Automated testing on all branches before merge
- Main branch protection with required status checks

**Commit Standards**:
- Descriptive commit messages with clear intent
- Atomic commits focusing on single changes
- Test inclusion with feature implementations
- Documentation updates with code changes

### 15.3 Code Quality Standards
**Development Guidelines**:
- Consistent code formatting and style
- Comprehensive error handling and validation
- Security-first development practices
- Performance considerations in design decisions

**Review Process**:
- Peer review for all code changes
- Automated code quality checks
- Security vulnerability scanning
- Performance impact assessment

### 15.4 CI/CD Pipeline Design
**Continuous Integration Requirements**:
- Automated testing on all commits and pull requests
- Code quality analysis and reporting
- Security vulnerability scanning
- Build verification and artifact generation

**Deployment Pipeline**:
- Automated deployment to staging environments
- Integration testing in staging
- Manual approval for production deployments
- Rollback capabilities for failed deployments

**Monitoring and Alerts**:
- Application performance monitoring
- Error tracking and alerting
- Security incident detection
- Usage analytics and reporting

## 16. Implementation Phases

### Phase 1-5: Foundation & Security

**Phase 1: Project Setup & Environment**
- Initialize Git repository with proper structure
- Set up development environment (Python, Node.js, Docker)
- Create basic project skeleton with folder structure
- Configure development tools (linting, formatting, pre-commit hooks)

**Phase 2: Secure Configuration System**
- Implement setup.py script for secure configuration
- Build encryption utilities for sensitive data storage
- Create configuration management service
- Test configuration encryption/decryption

**Phase 3: Authentication Framework**
- Implement HMAC-based API authentication
- Create JWT token management system
- Build authentication middleware
- Test authentication flows with mock requests

**Phase 4: Basic API Foundation**
- Set up FastAPI application with middleware
- Create basic health check endpoints
- Implement request/response models (Pydantic)
- Add error handling and validation framework

**Phase 5: Database & Session Management**
- Set up SQLite database for session storage
- Create session management service
- Implement progress tracking data models
- Test database operations and session lifecycle

### Phase 6-10: Core Processing Engine

**Phase 6: File Upload & Processing**
- Implement secure file upload endpoint
- Create resume parser for PDF/DOCX/TXT formats
- Add file validation and security checks
- Test with various resume formats and edge cases

**Phase 7: Claude API Integration**
- Set up Claude API client with error handling
- Create prompt template system
- Implement basic job description analysis
- Test Claude API integration with mock data

**Phase 8: Job Analysis Engine**
- Build job description parsing and analysis
- Extract key requirements, skills, and metadata
- Implement keyword extraction algorithms
- Test with diverse job descriptions

**Phase 9: Company Research Service**
- Implement web scraping for company information
- Create company data extraction and parsing
- Add rate limiting and respectful crawling
- Test with various company websites

**Phase 10: Resume Analysis & Enhancement**
- Build resume content analysis engine
- Implement skills gap analysis
- Create resume improvement recommendation system
- Test recommendation quality and relevance

### Phase 11-15: User Interface & Workflow

**Phase 11: Basic Frontend Setup**
- Create React application with TypeScript
- Set up component structure and routing
- Implement authentication service for frontend
- Create basic UI components and styling

**Phase 12: File Upload Interface**
- Build drag-and-drop file upload component
- Create job description input form
- Add input validation and user feedback
- Test file upload workflow end-to-end

**Phase 13: Progress Tracking System**
- Implement real-time progress tracking backend
- Create animated progress indicator component
- Add WebSocket or polling for live updates
- Test progress updates across workflow steps

**Phase 14: Results Display Interface**
- Create tabbed results display component
- Build resume recommendations visualization
- Implement cover letter display and editing
- Add company insights presentation

**Phase 15: Cover Letter Generation**
- Implement personalized cover letter creation
- Integrate company research into letter content
- Add tone and style customization options
- Test cover letter quality and personalization

### Phase 16-20: Production & Polish

**Phase 16: Comprehensive Testing**
- Implement full test suite (unit, integration, E2E)
- Add security testing and vulnerability checks
- Create performance testing and benchmarks
- Set up test automation and CI/CD pipeline

**Phase 17: Error Handling & Recovery**
- Implement comprehensive error handling
- Add retry mechanisms for failed operations
- Create user-friendly error messages
- Test failure scenarios and recovery flows

**Phase 18: Performance Optimization**
- Optimize file processing and Claude API calls
- Implement caching for company research
- Add request queuing for high load
- Performance testing and bottleneck resolution

**Phase 19: Security Hardening**
- Conduct security audit and penetration testing
- Implement rate limiting and abuse prevention
- Add monitoring and alerting systems
- Security documentation and incident response

**Phase 20: Production Deployment**
- Create Docker containers and orchestration
- Set up production environment and monitoring
- Implement backup and disaster recovery
- Launch with user documentation and support

### Implementation Strategy

**Milestone Deliverables**:
- **Phase 5**: Secure foundation with authentication
- **Phase 10**: Working backend processing engine
- **Phase 15**: Complete MVP with user interface
- **Phase 20**: Production-ready system

**Quality Gates**:
- Each phase includes comprehensive testing
- Security review at phases 5, 10, 15, and 19
- Performance validation at phases 10, 15, and 18
- User acceptance testing at phases 12, 14, and 15

**Risk Mitigation**:
- Early security implementation prevents rework
- Iterative testing catches issues early
- Progressive complexity reduces integration risks
- Modular architecture allows parallel development