// Test the API service similar to how the frontend would use it
const CryptoJS = require('crypto-js');

// Configuration (matching the frontend .env.local)
const config = {
    baseURL: 'http://localhost:8000',
    apiKey: 'yQ1sz7kmNo35R94vlMx3mw',
    apiSecret: 'MBClYvt6hptvZTj6ZCDXWlS10je29EJjYKgRd78xX24',
    timeout: 30000,
    maxRetries: 3,
    retryDelay: 1000,
};

// Simulate the CareerCraftApiService
class TestApiService {
    constructor(config) {
        this.config = config;
        this.jwtToken = null;
    }

    generateTimestamp() {
        return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
    }

    generateSignature(apiKey, timestamp, body) {
        const message = `${apiKey}\n${timestamp}\n${body}`;
        const signature = CryptoJS.HmacSHA256(message, this.config.apiSecret);
        return CryptoJS.enc.Base64.stringify(signature);
    }

    createAuthHeaders(body = '', contentType = 'application/json') {
        const timestamp = this.generateTimestamp();
        const signature = this.generateSignature(this.config.apiKey, timestamp, body);

        const headers = {
            'X-API-Key': this.config.apiKey,
            'X-Signature': signature,
            'X-Timestamp': timestamp,
            'Content-Type': contentType,
        };

        if (this.jwtToken) {
            headers.Authorization = `Bearer ${this.jwtToken}`;
        }

        return headers;
    }

    async makeRequest(method, endpoint, body = null, isFormData = false) {
        const url = `${this.config.baseURL}${endpoint}`;
        console.log(`Making ${method} request to: ${url}`);

        let requestBody;
        let headers;

        if (isFormData && body instanceof FormData) {
            requestBody = body;
            headers = this.createAuthHeaders('');
            delete headers['Content-Type'];
        } else if (body) {
            requestBody = JSON.stringify(body);
            headers = this.createAuthHeaders(requestBody);
        } else {
            requestBody = undefined;
            headers = this.createAuthHeaders('');
        }

        console.log('Headers:', headers);
        console.log('Body:', requestBody);

        try {
            const response = await fetch(url, {
                method,
                headers,
                body: requestBody,
            });

            console.log('Response status:', response.status);
            console.log('Response statusText:', response.statusText);

            const responseText = await response.text();
            console.log('Response body:', responseText);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${responseText}`);
            }

            return JSON.parse(responseText);
        } catch (error) {
            console.error('Request failed:', error);
            throw error;
        }
    }

    async login(request = {}) {
        console.log('\n=== Testing Login ===');
        const response = await this.makeRequest('POST', '/auth/login', request);
        this.jwtToken = response.access_token;
        console.log('Login successful, token received:', this.jwtToken ? 'Yes' : 'No');
        return response;
    }

    async healthCheck() {
        console.log('\n=== Testing Health Check ===');
        return await this.makeRequest('GET', '/health');
    }

    async startJobAnalysis(request, resumeFile = null) {
        console.log('\n=== Testing Job Analysis ===');
        
        if (resumeFile) {
            // FormData test
            const formData = new FormData();
            formData.append('job_description', request.job_description);
            if (request.job_url) {
                formData.append('job_url', request.job_url);
            }
            formData.append('tone', request.preferences.tone);
            formData.append('focus_areas', request.preferences.focus_areas.join(','));
            formData.append('include_salary_guidance', String(request.preferences.include_salary_guidance));
            formData.append('include_interview_prep', String(request.preferences.include_interview_prep));
            formData.append('resume_file', resumeFile);
            
            return await this.makeRequest('POST', '/api/v1/analyze-application', formData, true);
        } else {
            // JSON test
            return await this.makeRequest('POST', '/api/v1/analyze-application', request);
        }
    }
}

// Test the API service
async function runTests() {
    const apiService = new TestApiService(config);

    try {
        // Test 1: Health check
        await apiService.healthCheck();

        // Test 2: Login
        await apiService.login({
            client_id: 'test-client',
            permissions: ['read', 'write']
        });

        // Test 3: Job analysis (without file)
        const jobRequest = {
            job_description: 'Software Engineer position at a tech company',
            job_url: 'https://example.com/job',
            preferences: {
                tone: 'professional',
                focus_areas: ['technical_skills', 'experience'],
                include_salary_guidance: true,
                include_interview_prep: true
            }
        };

        await apiService.startJobAnalysis(jobRequest);

        console.log('\n✅ All tests passed!');
    } catch (error) {
        console.error('\n❌ Test failed:', error.message);
    }
}

runTests();