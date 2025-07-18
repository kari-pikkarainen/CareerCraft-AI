const crypto = require('crypto');

// Configuration from the backend
const API_KEY = 'yQ1sz7kmNo35R94vlMx3mw';
const API_SECRET = 'MBClYvt6hptvZTj6ZCDXWlS10je29EJjYKgRd78xX24';

// Generate timestamp in the format expected by backend
function generateTimestamp() {
    return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
}

// Generate HMAC-SHA256 signature
function generateSignature(apiKey, timestamp, body) {
    const message = `${apiKey}\n${timestamp}\n${body}`;
    const signature = crypto.createHmac('sha256', API_SECRET)
        .update(message)
        .digest('base64');
    return signature;
}

// Test the signature generation
const timestamp = generateTimestamp();
const body = '';
const signature = generateSignature(API_KEY, timestamp, body);

console.log('Testing HMAC signature generation:');
console.log('API Key:', API_KEY);
console.log('Timestamp:', timestamp);
console.log('Body:', body);
console.log('Signature:', signature);
console.log('\nHeaders would be:');
console.log('X-API-Key:', API_KEY);
console.log('X-Timestamp:', timestamp);
console.log('X-Signature:', signature);

// Test with a health check request
const testHealthCheck = async () => {
    try {
        const response = await fetch('http://localhost:8000/health', {
            method: 'GET',
            headers: {
                'X-API-Key': API_KEY,
                'X-Timestamp': timestamp,
                'X-Signature': signature,
                'Content-Type': 'application/json'
            }
        });
        
        console.log('\nHealth check response:');
        console.log('Status:', response.status);
        console.log('Status Text:', response.statusText);
        
        if (response.ok) {
            const data = await response.json();
            console.log('Data:', data);
        } else {
            const error = await response.text();
            console.log('Error:', error);
        }
    } catch (error) {
        console.error('Request failed:', error);
    }
};

testHealthCheck();