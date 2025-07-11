/**
 * Local Development Page - No Authentication Required
 * Direct access to job analysis workflow for testing
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2024 Kari Pikkarainen. All rights reserved.
 */

import React from 'react';
import './LocalDevelopmentPage.css';

const LocalDevelopmentPage: React.FC = () => {

  return (
    <div className="local-dev-page">
      {/* Header */}
      <header className="local-dev-header">
        <div className="container">
          <div className="header-content">
            <div className="logo">
              <span className="logo-icon">🧪</span>
              <span className="logo-text">CareerCraft AI - Local Development</span>
            </div>
            <div className="dev-badge">
              <span className="status-indicator"></span>
              Development Mode
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="local-dev-main">
        <div className="container">
          {/* Welcome Section */}
          <section className="welcome-section">
            <h1>🚀 Local Development Environment</h1>
            <p className="welcome-description">
              Welcome to the CareerCraft AI local development environment. 
              This interface bypasses authentication to enable rapid testing of core job analysis features.
            </p>
            
            <div className="dev-info-grid">
              <div className="dev-info-card">
                <div className="info-icon">⚡</div>
                <h3>Fast Iteration</h3>
                <p>No authentication barriers - direct access to all features</p>
              </div>
              
              <div className="dev-info-card">
                <div className="info-icon">🔧</div>
                <h3>Full API Access</h3>
                <p>Complete backend integration with real-time debugging</p>
              </div>
              
              <div className="dev-info-card">
                <div className="info-icon">🎯</div>
                <h3>Core Features</h3>
                <p>Test the complete 7-step job analysis workflow</p>
              </div>
            </div>
          </section>

          {/* Quick Actions */}
          <section className="quick-actions-section">
            <h2>🛠️ Development Tools</h2>
            
            <div className="actions-grid">
              <div className="action-card">
                <h3>📋 Job Analysis Workflow</h3>
                <p>Test the complete job analysis process from start to finish</p>
                <button className="btn btn-primary" onClick={() => window.location.href = '/local/analyze'}>
                  Start Job Analysis
                </button>
              </div>
              
              <div className="action-card">
                <h3>📁 File Upload Testing</h3>
                <p>Test resume file upload and processing capabilities</p>
                <button className="btn btn-secondary" onClick={() => window.location.href = '/local/upload'}>
                  Test File Upload
                </button>
              </div>
              
              <div className="action-card">
                <h3>📊 Progress Tracking</h3>
                <p>View real-time progress updates during analysis</p>
                <button className="btn btn-secondary" onClick={() => window.location.href = '/local/progress'}>
                  View Progress Demo
                </button>
              </div>
              
              <div className="action-card">
                <h3>📈 Results Display</h3>
                <p>Preview analysis results and recommendations</p>
                <button className="btn btn-secondary" onClick={() => window.location.href = '/local/results'}>
                  View Sample Results
                </button>
              </div>
              
              <div className="action-card">
                <h3>🔧 API Connection Test</h3>
                <p>Test backend API connectivity and authentication</p>
                <button className="btn btn-secondary" onClick={() => window.location.href = '/local/api-test'}>
                  Test API Connection
                </button>
              </div>
              
              <div className="action-card">
                <h3>🧪 End-to-End Testing</h3>
                <p>Comprehensive workflow testing and validation</p>
                <button className="btn btn-secondary" onClick={() => window.location.href = '/local/test'}>
                  Run Workflow Tests
                </button>
              </div>
            </div>
          </section>

          {/* API Status */}
          <section className="api-status-section">
            <h2>🔌 API Connection Status</h2>
            
            <div className="status-card">
              <div className="status-header">
                <h3>Backend API</h3>
                <div className="status-indicator-wrapper">
                  <div className="status-indicator connected"></div>
                  <span>Connected</span>
                </div>
              </div>
              
              <div className="status-details">
                <div className="detail-item">
                  <span className="detail-label">Base URL:</span>
                  <span className="detail-value">http://localhost:8000</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Authentication:</span>
                  <span className="detail-value">Bypassed for development</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Available Endpoints:</span>
                  <span className="detail-value">All endpoints accessible</span>
                </div>
              </div>
              
              <div className="status-actions">
                <button className="btn btn-outline">Test Connection</button>
                <button className="btn btn-outline">View API Docs</button>
              </div>
            </div>
          </section>

          {/* Development Notes */}
          <section className="dev-notes-section">
            <h2>📝 Development Notes</h2>
            
            <div className="notes-content">
              <div className="note-item">
                <h4>🎯 Current Focus</h4>
                <p>Building core job analysis workflow without authentication complexity</p>
              </div>
              
              <div className="note-item">
                <h4>🔧 Next Steps</h4>
                <ul>
                  <li>Implement file upload component with drag-and-drop</li>
                  <li>Build job description input form</li>
                  <li>Create real-time progress tracking UI</li>
                  <li>Build results display components</li>
                </ul>
              </div>
              
              <div className="note-item">
                <h4>⚠️ Important</h4>
                <p>This is a development-only interface. Authentication will be added for production use.</p>
              </div>
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="local-dev-footer">
        <div className="container">
          <p>&copy; 2024 Kari Pikkarainen. CareerCraft AI - Local Development Environment</p>
        </div>
      </footer>
    </div>
  );
};

export default LocalDevelopmentPage;