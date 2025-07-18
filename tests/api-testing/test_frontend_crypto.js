// Test crypto-js implementation matching the frontend
const CryptoJS = require('crypto-js');

// Configuration from the backend
const API_KEY = 'yQ1sz7kmNo35R94vlMx3mw';
const API_SECRET = 'MBClYvt6hptvZTj6ZCDXWlS10je29EJjYKgRd78xX24';

// Generate ISO timestamp in the format expected by backend
function generateTimestamp() {
    return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
}

// Generate HMAC-SHA256 signature using crypto-js (frontend implementation)
function generateSignature(apiKey, timestamp, body) {
    // Create message in exact format expected by backend: api_key + "\n" + timestamp + "\n" + body
    const message = `${apiKey}\n${timestamp}\n${body}`;
    
    // Generate HMAC-SHA256 signature
    const signature = CryptoJS.HmacSHA256(message, API_SECRET);
    
    // Convert to Base64 string
    return CryptoJS.enc.Base64.stringify(signature);
}

// Test the signature generation
const timestamp = generateTimestamp();
const body = '';
const signature = generateSignature(API_KEY, timestamp, body);

console.log('Testing crypto-js signature generation:');
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

// Test with authentication
const testAuth = async () => {
    try {
        const authBody = JSON.stringify({});
        const authTimestamp = generateTimestamp();
        const authSignature = generateSignature(API_KEY, authTimestamp, authBody);
        
        console.log('\nTesting authentication:');
        console.log('Auth Body:', authBody);
        console.log('Auth Timestamp:', authTimestamp);
        console.log('Auth Signature:', authSignature);
        
        const response = await fetch('http://localhost:8000/auth/login', {
            method: 'POST',
            headers: {
                'X-API-Key': API_KEY,
                'X-Timestamp': authTimestamp,
                'X-Signature': authSignature,
                'Content-Type': 'application/json'
            },
            body: authBody
        });
        
        console.log('\nAuth response:');
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
        console.error('Auth request failed:', error);
    }
};

testHealthCheck().then(() => testAuth());