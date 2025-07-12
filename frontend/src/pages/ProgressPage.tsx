/**
 * Progress Page - Real-time job analysis progress tracking
 * Shows 7-step workflow progress with live updates
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import ProgressTracker from '../components/ProgressTracker';
import './ProgressPage.css';

interface AnalysisData {
  jobTitle: string;
  companyName: string;
  resumeFileName: string;
  jobDescription: string;
  analysisId?: string;
}

const ProgressPage: React.FC = () => {
  const navigate = useNavigate();
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [isProgressActive, setIsProgressActive] = useState(false);
  const [showControls, setShowControls] = useState(true);

  // Demo data for testing
  const getDemoData = useCallback((): AnalysisData => ({
    jobTitle: 'Senior Software Engineer',
    companyName: 'TechCorp Inc.',
    resumeFileName: 'john_doe_resume.pdf',
    jobDescription: 'We are looking for a skilled Senior Software Engineer...',
    analysisId: 'demo-analysis-' + Date.now(),
  }), []);

  // Load analysis data from session storage or use demo data
  useEffect(() => {
    const storedData = sessionStorage.getItem('analysisData');
    if (storedData) {
      try {
        setAnalysisData(JSON.parse(storedData));
      } catch (error) {
        console.error('Failed to parse analysis data:', error);
        setAnalysisData(getDemoData());
      }
    } else {
      setAnalysisData(getDemoData());
    }
  }, [getDemoData]);

  // Handle analysis completion
  const handleAnalysisComplete = useCallback(() => {
    console.log('Analysis completed successfully');
    
    // Store completion status
    sessionStorage.setItem('analysisCompleted', 'true');
    sessionStorage.setItem('analysisCompletedAt', new Date().toISOString());
    
    // Navigate to results page
    setTimeout(() => {
      navigate('/local/results');
    }, 2000);
  }, [navigate]);

  // Handle analysis error
  const handleAnalysisError = useCallback((error: string) => {
    console.error('Analysis failed:', error);
    
    // Store error status
    sessionStorage.setItem('analysisError', error);
    sessionStorage.setItem('analysisErrorAt', new Date().toISOString());
  }, []);

  // Start analysis
  const handleStartAnalysis = useCallback(() => {
    setIsProgressActive(true);
    setShowControls(false);
    
    // Store analysis start time
    sessionStorage.setItem('analysisStarted', 'true');
    sessionStorage.setItem('analysisStartedAt', new Date().toISOString());
  }, []);

  // Cancel analysis
  const handleCancelAnalysis = useCallback(() => {
    setIsProgressActive(false);
    setShowControls(true);
    
    // Clear analysis status
    sessionStorage.removeItem('analysisStarted');
    sessionStorage.removeItem('analysisStartedAt');
  }, []);

  // Go back to analysis setup
  const handleGoBack = useCallback(() => {
    navigate('/local/analyze');
  }, [navigate]);

  // Reset and start new analysis
  const handleStartNew = useCallback(() => {
    // Clear all analysis data
    sessionStorage.removeItem('analysisData');
    sessionStorage.removeItem('analysisStarted');
    sessionStorage.removeItem('analysisCompleted');
    sessionStorage.removeItem('analysisError');
    
    navigate('/local/analyze');
  }, [navigate]);

  if (!analysisData) {
    return (
      <div className="progress-page loading">
        <div className="loading-content">
          <div className="spinner-large"></div>
          <p>Loading analysis data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="progress-page">
      {/* Header */}
      <header className="progress-header">
        <div className="container">
          <div className="header-content">
            <div className="breadcrumb">
              <a href="/local" className="breadcrumb-link">🧪 Local Development</a>
              <span className="breadcrumb-separator">›</span>
              <a href="/local/analyze" className="breadcrumb-link">🎯 Job Analysis</a>
              <span className="breadcrumb-separator">›</span>
              <span className="breadcrumb-current">📊 Progress Tracking</span>
            </div>
            <h1>Real-Time Analysis Progress</h1>
            <p className="page-description">
              Watch as AI analyzes your job application in real-time
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="progress-main">
        <div className="container">
          {/* Control Panel */}
          {showControls && (
            <div className="control-panel">
              <div className="panel-header">
                <h2>🚀 Ready to Start Analysis</h2>
                <p>Click below to begin the AI-powered job analysis workflow</p>
              </div>
              
              <div className="analysis-summary">
                <div className="summary-grid">
                  <div className="summary-item">
                    <span className="summary-label">Position</span>
                    <span className="summary-value">{analysisData.jobTitle}</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">Company</span>
                    <span className="summary-value">{analysisData.companyName}</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">Resume</span>
                    <span className="summary-value">{analysisData.resumeFileName}</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">Process</span>
                    <span className="summary-value">7-Step AI Analysis</span>
                  </div>
                </div>
              </div>

              <div className="control-actions">
                <button
                  className="btn btn-primary btn-large"
                  onClick={handleStartAnalysis}
                >
                  <span className="btn-icon">🚀</span>
                  Start AI Analysis
                </button>
                
                <button
                  className="btn btn-outline"
                  onClick={handleGoBack}
                >
                  <span className="btn-icon">←</span>
                  Back to Setup
                </button>
              </div>
            </div>
          )}

          {/* Progress Tracker */}
          {isProgressActive && (
            <div className="progress-section">
              <ProgressTracker
                isActive={isProgressActive}
                onComplete={handleAnalysisComplete}
                onError={handleAnalysisError}
                simulateProgress={true}
                analysisData={{
                  jobTitle: analysisData.jobTitle,
                  companyName: analysisData.companyName,
                  resumeFileName: analysisData.resumeFileName,
                }}
              />
              
              {/* Emergency Controls */}
              <div className="emergency-controls">
                <button
                  className="btn btn-outline btn-small"
                  onClick={handleCancelAnalysis}
                >
                  <span className="btn-icon">⏹️</span>
                  Cancel Analysis
                </button>
              </div>
            </div>
          )}

          {/* Information Panel */}
          <div className="info-panel">
            <h3>🔍 What Happens During Analysis</h3>
            
            <div className="info-grid">
              <div className="info-card">
                <div className="info-icon">📋</div>
                <h4>Job Analysis</h4>
                <p>Extract requirements, skills, and keywords from the job posting using advanced NLP</p>
              </div>
              
              <div className="info-card">
                <div className="info-icon">🏢</div>
                <h4>Company Research</h4>
                <p>Research company culture, values, and insights to tailor your application</p>
              </div>
              
              <div className="info-card">
                <div className="info-icon">📄</div>
                <h4>Resume Parsing</h4>
                <p>Intelligent parsing and structuring of your resume content</p>
              </div>
              
              <div className="info-card">
                <div className="info-icon">🔍</div>
                <h4>Skills Analysis</h4>
                <p>Compare your skills against job requirements and identify gaps</p>
              </div>
              
              <div className="info-card">
                <div className="info-icon">💡</div>
                <h4>Enhancement</h4>
                <p>Generate personalized recommendations to improve your application</p>
              </div>
              
              <div className="info-card">
                <div className="info-icon">✉️</div>
                <h4>Cover Letter</h4>
                <p>Create a tailored cover letter that highlights your strengths</p>
              </div>
            </div>
          </div>

          {/* Development Notes */}
          <div className="dev-notes">
            <h3>🔧 Development Notes</h3>
            <div className="notes-content">
              <div className="note-item">
                <strong>Progress Simulation:</strong> This demo uses simulated progress for testing the UI components
              </div>
              <div className="note-item">
                <strong>Real Integration:</strong> In production, this will connect to the actual Claude API workflow
              </div>
              <div className="note-item">
                <strong>Time Estimates:</strong> Actual processing times may vary based on job complexity and resume length
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="progress-footer">
        <div className="container">
          <div className="footer-content">
            <p>&copy; 2025 Kari Pikkarainen. CareerCraft AI - Local Development</p>
            <div className="footer-actions">
              <button 
                className="btn btn-outline btn-small"
                onClick={handleStartNew}
              >
                <span className="btn-icon">🔄</span>
                Start New Analysis
              </button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default ProgressPage;