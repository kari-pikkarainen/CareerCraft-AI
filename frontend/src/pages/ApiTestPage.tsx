/**
 * API Test Page - Test API connection and authentication
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

import React, { useState, useEffect } from 'react';
import { configService } from '../services/configService';

const ApiTestPage: React.FC = () => {
  const [config, setConfig] = useState<any>(null);
  const [healthStatus, setHealthStatus] = useState<any>(null);
  const [authStatus, setAuthStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Load configuration
    const appConfig = configService.getConfig();
    setConfig(appConfig);
  }, []);

  const testHealthEndpoint = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${config.api.baseURL}/health`);
      const data = await response.json();
      setHealthStatus({
        status: response.status,
        data: data
      });
    } catch (err) {
      setError(`Health check failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const testAuthentication = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Create HMAC signature
      const timestamp = new Date().toISOString();
      const body = JSON.stringify({
        client_id: 'frontend-test',
        permissions: ['read']
      });
      
      const message = `${config.api.apiKey}\n${timestamp}\n${body}`;
      
      // Use Web Crypto API for HMAC
      const encoder = new TextEncoder();
      const keyData = encoder.encode(config.api.apiSecret);
      const messageData = encoder.encode(message);
      
      const cryptoKey = await crypto.subtle.importKey(
        'raw',
        keyData,
        { name: 'HMAC', hash: 'SHA-256' },
        false,
        ['sign']
      );
      
      const signature = await crypto.subtle.sign('HMAC', cryptoKey, messageData);
      const signatureArray = Array.from(new Uint8Array(signature));
      const signatureBase64 = btoa(String.fromCharCode.apply(null, signatureArray));
      
      const response = await fetch(`${config.api.baseURL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': config.api.apiKey,
          'X-Signature': signatureBase64,
          'X-Timestamp': timestamp,
        },
        body: body
      });
      
      const data = await response.json();
      setAuthStatus({
        status: response.status,
        data: data,
        headers: {
          'X-API-Key': config.api.apiKey.substring(0, 10) + '...',
          'X-Signature': signatureBase64.substring(0, 20) + '...',
          'X-Timestamp': timestamp
        }
      });
    } catch (err) {
      setError(`Authentication test failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1>🧪 API Connection Test</h1>
      
      {/* Configuration Display */}
      <div style={{ background: '#f5f5f5', padding: '1rem', borderRadius: '8px', marginBottom: '2rem' }}>
        <h2>📋 Configuration</h2>
        {config ? (
          <pre style={{ background: '#fff', padding: '1rem', borderRadius: '4px', overflow: 'auto' }}>
            {JSON.stringify({
              ...config,
              api: {
                ...config.api,
                apiKey: config.api.apiKey ? config.api.apiKey.substring(0, 10) + '...' : 'Not set',
                apiSecret: config.api.apiSecret ? config.api.apiSecret.substring(0, 10) + '...' : 'Not set'
              }
            }, null, 2)}
          </pre>
        ) : (
          <p>Loading configuration...</p>
        )}
      </div>

      {/* Test Buttons */}
      <div style={{ marginBottom: '2rem' }}>
        <button 
          onClick={testHealthEndpoint}
          disabled={loading || !config}
          style={{ 
            padding: '0.75rem 1.5rem', 
            marginRight: '1rem', 
            backgroundColor: '#3182ce', 
            color: 'white', 
            border: 'none', 
            borderRadius: '6px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Testing...' : '🩺 Test Health Endpoint'}
        </button>
        
        <button 
          onClick={testAuthentication}
          disabled={loading || !config || !config.api.apiKey || !config.api.apiSecret}
          style={{ 
            padding: '0.75rem 1.5rem', 
            backgroundColor: '#38a169', 
            color: 'white', 
            border: 'none', 
            borderRadius: '6px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Testing...' : '🔐 Test Authentication'}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div style={{ background: '#fed7d7', padding: '1rem', borderRadius: '8px', marginBottom: '2rem', color: '#c53030' }}>
          <h3>❌ Error</h3>
          <p>{error}</p>
        </div>
      )}

      {/* Health Status */}
      {healthStatus && (
        <div style={{ background: '#f0fff4', padding: '1rem', borderRadius: '8px', marginBottom: '2rem' }}>
          <h3>🩺 Health Check Results</h3>
          <p><strong>Status:</strong> {healthStatus.status}</p>
          <pre style={{ background: '#fff', padding: '1rem', borderRadius: '4px', overflow: 'auto' }}>
            {JSON.stringify(healthStatus.data, null, 2)}
          </pre>
        </div>
      )}

      {/* Auth Status */}
      {authStatus && (
        <div style={{ 
          background: authStatus.status === 200 ? '#f0fff4' : '#fed7d7', 
          padding: '1rem', 
          borderRadius: '8px', 
          marginBottom: '2rem' 
        }}>
          <h3>🔐 Authentication Test Results</h3>
          <p><strong>Status:</strong> {authStatus.status}</p>
          
          <h4>Request Headers:</h4>
          <pre style={{ background: '#fff', padding: '1rem', borderRadius: '4px', overflow: 'auto' }}>
            {JSON.stringify(authStatus.headers, null, 2)}
          </pre>
          
          <h4>Response:</h4>
          <pre style={{ background: '#fff', padding: '1rem', borderRadius: '4px', overflow: 'auto' }}>
            {JSON.stringify(authStatus.data, null, 2)}
          </pre>
        </div>
      )}

      {/* Instructions */}
      <div style={{ background: '#ebf8ff', padding: '1rem', borderRadius: '8px' }}>
        <h3>📝 Instructions</h3>
        <ol>
          <li>Check that the configuration shows valid API credentials</li>
          <li>Test the health endpoint (should return 200 status)</li>
          <li>Test authentication (should return 200 with session token)</li>
          <li>If authentication fails, check the backend logs for details</li>
        </ol>
      </div>
    </div>
  );
};

export default ApiTestPage;