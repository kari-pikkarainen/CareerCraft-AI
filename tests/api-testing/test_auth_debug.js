// Debug authentication issues with detailed logging
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
    const message = `${apiKey}\n${timestamp}\n${body}`;
    const signature = CryptoJS.HmacSHA256(message, API_SECRET);
    return CryptoJS.enc.Base64.stringify(signature);
}

// Test with different body formats
async function testAuthVariations() {
    const bodies = [
        '{}',
        JSON.stringify({}),
        JSON.stringify({client_id: 'test'}),
        JSON.stringify({client_id: 'test', permissions: ['read']}),
        ''
    ];
    
    for (const body of bodies) {
        console.log('\n' + '='.repeat(60));
        console.log(`Testing with body: "${body}"`);
        
        const timestamp = generateTimestamp();
        const signature = generateSignature(API_KEY, timestamp, body);
        
        console.log('Timestamp:', timestamp);
        console.log('Signature:', signature);
        
        try {
            const response = await fetch('http://localhost:8000/auth/login', {
                method: 'POST',
                headers: {
                    'X-API-Key': API_KEY,
                    'X-Timestamp': timestamp,
                    'X-Signature': signature,
                    'Content-Type': 'application/json'
                },
                body: body
            });
            
            console.log('Status:', response.status);
            console.log('Status Text:', response.statusText);
            
            const responseText = await response.text();
            console.log('Response:', responseText);
            
            // If successful, parse as JSON
            if (response.ok) {
                try {
                    const data = JSON.parse(responseText);
                    console.log('Parsed data:', data);
                    break; // Success, exit loop
                } catch (e) {
                    console.log('Failed to parse JSON:', e.message);
                }
            }
        } catch (error) {
            console.error('Request failed:', error.message);
        }
    }
}

testAuthVariations();