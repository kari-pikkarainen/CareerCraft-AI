# Test Organization

This directory contains various types of tests for the CareerCraft AI project.

## Directory Structure

### `/api-testing/`
JavaScript files for testing API endpoints and authentication:
- `test_api_call.js` - Basic API call testing
- `test_api_service.js` - API service integration testing  
- `test_auth_debug.js` - Authentication debugging tools
- `test_auth_simple.js` - Simple authentication testing
- `test_frontend_crypto.js` - Frontend cryptography testing
- `test_frontend_workflow.js` - Frontend workflow testing
- `test_hmac_signature.js` - HMAC signature validation

### `/scripts/`
Shell scripts for testing and automation:
- `test_curl_auth.sh` - cURL-based authentication testing

### `/manual/`
Manual testing configurations and dependencies:
- `package.json` - Node.js dependencies for manual testing
- `package-lock.json` - Locked dependency versions

### `/e2e/`
End-to-end testing (placeholder for future implementation)

### `/integration/`
Integration testing (placeholder for future implementation)

## Usage

### API Testing
```bash
cd tests/api-testing
node test_api_call.js
```

### Authentication Testing
```bash
cd tests/scripts
./test_curl_auth.sh
```

### Manual Testing Setup
```bash
cd tests/manual
npm install
```

## Notes

- API testing requires the backend to be running on localhost:8000
- Authentication tests use the credentials from backend setup
- Manual tests may require additional configuration files