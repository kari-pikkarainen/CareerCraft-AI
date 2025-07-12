/**
 * Test Page - End-to-End Workflow Testing
 * Comprehensive testing interface for the complete workflow
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

import React from 'react';
import WorkflowTest from '../tests/WorkflowTest';
import './TestPage.css';

const TestPage: React.FC = () => {
  return (
    <div className="test-page">
      {/* Header */}
      <header className="test-page-header">
        <div className="container">
          <div className="header-content">
            <div className="breadcrumb">
              <a href="/local" className="breadcrumb-link">🧪 Local Development</a>
              <span className="breadcrumb-separator">›</span>
              <span className="breadcrumb-current">🔧 End-to-End Tests</span>
            </div>
            <h1>Workflow Testing Suite</h1>
            <p className="page-description">
              Comprehensive testing of the complete job analysis workflow
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="test-page-main">
        <div className="container">
          <WorkflowTest />
        </div>
      </main>

      {/* Footer */}
      <footer className="test-page-footer">
        <div className="container">
          <div className="footer-content">
            <p>&copy; 2025 Kari Pikkarainen. CareerCraft AI - Local Development</p>
            <div className="footer-links">
              <a href="/local" className="footer-link">← Back to Development</a>
              <a href="/local/analyze" className="footer-link">Start Analysis</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default TestPage;