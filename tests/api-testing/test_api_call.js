const crypto = require('crypto');

// API configuration from frontend .env.local
const API_BASE_URL = 'http://localhost:8000';
const API_KEY = 'yQ1sz7kmNo35R94vlMx3mw';
const API_SECRET = 'MBClYvt6hptvZTj6ZCDXWlS10je29EJjYKgRd78xX24';

// Generate HMAC signature like the frontend does
function generateSignature(apiKey, timestamp, body) {
    const message = `${apiKey}\n${timestamp}\n${body}`;
    const signature = crypto.createHmac('sha256', API_SECRET).update(message).digest('base64');
    return signature;
}

// Generate timestamp
function generateTimestamp() {
    return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
}

// Test API call
async function testApiCall() {
    // Create form data
    const formData = new FormData();
    formData.append('job_description', 'Software Engineer position at a tech company. Looking for React and Node.js experience.');
    formData.append('resume_text', 'John Doe\nSenior Software Engineer\n\nExperience:\n- 5 years React development\n- 3 years Node.js\n- Full-stack development\n\nSkills:\n- JavaScript, TypeScript\n- React, Vue.js\n- Node.js, Express\n- MongoDB, PostgreSQL');
    formData.append('tone', 'professional');
    formData.append('focus_areas', 'relevant experience,technical skills');
    formData.append('include_salary_guidance', 'true');
    formData.append('include_interview_prep', 'true');

    // For form data, use empty body for signature
    const bodyForSignature = '';
    const timestamp = generateTimestamp();
    const signature = generateSignature(API_KEY, timestamp, bodyForSignature);

    console.log('🧪 Testing API call to:', `${API_BASE_URL}/api/v1/analyze-application`);
    console.log('📝 Form data fields:', Array.from(formData.keys()));
    console.log('🔑 API Key:', API_KEY);
    console.log('⏰ Timestamp:', timestamp);
    console.log('✍️  Signature:', signature);

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/analyze-application`, {
            method: 'POST',
            headers: {
                'X-API-Key': API_KEY,
                'X-Timestamp': timestamp,
                'X-Signature': signature,
                // Don't set Content-Type for FormData - browser sets it with boundary
            },
            body: formData
        });

        console.log('📊 Response status:', response.status);
        console.log('📋 Response headers:', Object.fromEntries(response.headers.entries()));

        const data = await response.json();
        console.log('💾 Response data:', JSON.stringify(data, null, 2));

        if (response.ok) {
            console.log('✅ API call successful! Check backend console for Claude API logs.');
        } else {
            console.log('❌ API call failed:', data);
        }
    } catch (error) {
        console.error('🚨 API call error:', error);
    }
}

testApiCall().catch(console.error);