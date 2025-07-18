// Simple auth test to understand the 400 error
const CryptoJS = require('crypto-js');

// Configuration
const API_KEY = 'yQ1sz7kmNo35R94vlMx3mw';
const API_SECRET = 'MBClYvt6hptvZTj6ZCDXWlS10je29EJjYKgRd78xX24';

function generateTimestamp() {
    return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
}

function generateSignature(apiKey, timestamp, body) {
    const message = `${apiKey}\n${timestamp}\n${body}`;
    const signature = CryptoJS.HmacSHA256(message, API_SECRET);
    return CryptoJS.enc.Base64.stringify(signature);
}

async function testAuth() {
    const body = JSON.stringify({
        client_id: 'test-client',
        permissions: ['read', 'write']
    });
    
    const timestamp = generateTimestamp();
    const signature = generateSignature(API_KEY, timestamp, body);
    
    console.log('Testing auth with:');
    console.log('Body:', body);
    console.log('Timestamp:', timestamp);
    console.log('Signature:', signature);
    
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
        
        const response = await fetch('http://localhost:8000/auth/login', {
            method: 'POST',
            headers: {
                'X-API-Key': API_KEY,
                'X-Timestamp': timestamp,
                'X-Signature': signature,
                'Content-Type': 'application/json'
            },
            body: body,
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        console.log('Status:', response.status);
        console.log('StatusText:', response.statusText);
        console.log('Headers:', Object.fromEntries(response.headers.entries()));
        
        const responseText = await response.text();
        console.log('Response:', responseText);
        
        if (response.ok) {
            const data = JSON.parse(responseText);
            console.log('Success! Token received:', data.access_token ? 'Yes' : 'No');
        } else {
            console.log('Failed with status:', response.status);
            try {
                const errorData = JSON.parse(responseText);
                console.log('Error data:', errorData);
            } catch (e) {
                console.log('Could not parse error response as JSON');
            }
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            console.error('Request timed out');
        } else {
            console.error('Request failed:', error);
        }
    }
}

testAuth();