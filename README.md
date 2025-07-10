# CareerCraft AI

An intelligent job application assistant that uses Claude API to analyze job descriptions, research companies, and generate personalized resume recommendations and cover letters.

## Features

- **Job Description Analysis**: Extract key requirements and skills from job postings
- **Company Research**: Automated web research for company insights and culture
- **Resume Enhancement**: AI-powered improvement suggestions and keyword optimization
- **Cover Letter Generation**: Personalized cover letters based on job and company analysis
- **Real-time Progress Tracking**: 7-step workflow with live progress updates
- **Secure Architecture**: HMAC-based authentication with encrypted configuration

## Tech Stack

- **Backend**: Python 3.9+ with FastAPI
- **Frontend**: React.js with TypeScript
- **AI Integration**: Anthropic Claude API
- **Database**: SQLite for session storage
- **Security**: Encrypted configuration, HMAC authentication, JWT sessions

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
uvicorn main:app --reload
```

### Frontend Setup

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

The application will be available at `http://localhost:3000`

## API Authentication

All API requests require authentication headers:
```
X-API-Key: your_api_key
X-Signature: hmac_sha256_signature
X-Timestamp: 2025-07-10T10:30:00Z
```

## Development

### Running Tests

Backend tests:
```bash
cd backend
pytest
```

Frontend tests:
```bash
cd frontend
npm test
```

### Code Quality

Backend linting:
```bash
cd backend
black .
flake8 .
mypy .
```

Frontend linting:
```bash
cd frontend
npm run lint
npm run type-check
```

## Project Structure

```
CareerCraft-AI/
├── backend/                 # Python FastAPI backend
│   ├── config/             # Configuration management
│   ├── agents/             # AI agent orchestration
│   ├── api/                # API endpoints and models
│   ├── services/           # Business logic services
│   └── utils/              # Utility functions
├── frontend/               # React TypeScript frontend
│   └── src/
│       ├── components/     # UI components
│       ├── pages/          # Page components
│       ├── services/       # API and auth services
│       └── types/          # TypeScript definitions
└── tests/                  # Integration and E2E tests
```

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

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions, please open an issue in the GitHub repository.