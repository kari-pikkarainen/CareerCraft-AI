# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CareerCraft AI is an intelligent job application assistant that uses Claude API to analyze job descriptions, research companies, and generate personalized resume recommendations and cover letters. The project is currently in the planning phase with a comprehensive technical specification but no implemented code.

## Architecture

### Planned Tech Stack
- **Backend**: Python 3.9+ with FastAPI
- **Frontend**: React.js with TypeScript  
- **AI Integration**: Anthropic Claude API
- **Database**: SQLite for session storage
- **Deployment**: Docker containers

### Security Architecture
- HMAC-based API authentication with JWT session management
- Encrypted configuration storage using Fernet encryption
- Setup script (`setup.py`) for secure initialization of credentials
- All API requests require signed headers: `X-API-Key`, `X-Signature`, `X-Timestamp`

## Core Workflow

The system implements a 7-step processing pipeline:
1. Job Description Analysis (14%) - Extract requirements and metadata
2. Company Research (28%) - Web scraping for company insights  
3. Resume Parsing (42%) - Extract content from PDF/DOCX/TXT files
4. Skills Gap Analysis (57%) - Compare resume vs job requirements
5. Resume Enhancement (71%) - Generate improvement suggestions
6. Cover Letter Generation (85%) - Create personalized cover letters
7. Final Review & Formatting (100%) - Quality check and formatting

## Key API Endpoints

- `POST /api/v1/analyze-application` - Main processing endpoint
- `GET /api/v1/status/{session_id}` - Real-time progress tracking
- `GET /api/v1/results/{session_id}` - Retrieve completed analysis
- `GET /api/v1/history` - Application history
- `DELETE /api/v1/session/{session_id}` - Session cleanup

## Implementation Status

**Current State**: Project exists only as specification (`job_agent_spec.md`)
- No code implementation yet
- No project structure created
- Git repository not initialized

**Required Setup Before Development**:
1. Initialize git repository
2. Create backend/ and frontend/ directory structure
3. Set up development environment (Python 3.9+, Node.js)
4. Implement the secure setup script first (Phase 2 in spec)

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

## File Processing

- **Supported formats**: PDF (PyPDF2), DOCX (python-docx), TXT
- **Size limits**: Maximum 10MB file uploads
- **Temporary storage**: Files auto-deleted after processing
- **Parser requirements**: Extract sections (experience, skills, education, contact info)

## Testing Strategy

Test-driven development with:
- **Unit tests**: Individual functions and security components
- **Integration tests**: API endpoints and Claude API integration  
- **E2E tests**: Complete workflow from upload to results
- **Security tests**: Authentication bypass attempts, file upload security
- **Performance tests**: File processing times, concurrent user handling

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