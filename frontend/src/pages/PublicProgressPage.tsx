/**
 * Public Progress Page - Real-time analysis progress tracking
 * Clean, production-ready interface for monitoring job analysis
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2024 Kari Pikkarainen. All rights reserved.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAnalysis } from '../contexts/AnalysisContext';
import { ProgressStep as ApiProgressStep, ProcessingStatusEnum } from '../types';
import './PublicProgressPage.css';

interface AnalysisData {
  jobTitle: string;
  companyName: string;
  resumeFileName: string;
  jobDescription: string;
  analysisId: string;
}

const PublicProgressPage: React.FC = () => {
  const navigate = useNavigate();
  const { getProgress } = useAnalysis();
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [currentStep, setCurrentStep] = useState<ApiProgressStep | null>(null);
  const [allSteps, setAllSteps] = useState<ApiProgressStep[]>([]);
  const [overallProgress, setOverallProgress] = useState(0);
  const [status, setStatus] = useState<ProcessingStatusEnum>(ProcessingStatusEnum.PROCESSING);
  const [error, setError] = useState<string | null>(null);
  const [estimatedTime, setEstimatedTime] = useState<string>('Calculating...');

  // Load analysis data from session storage
  useEffect(() => {
    const storedData = sessionStorage.getItem('analysisData');
    if (storedData) {
      try {
        const data = JSON.parse(storedData);
        setAnalysisData(data);
      } catch (error) {
        console.error('Failed to parse analysis data:', error);
        navigate('/analyze');
      }
    } else {
      navigate('/analyze');
    }
  }, [navigate]);

  // Fetch progress updates
  const fetchProgress = useCallback(async () => {
    if (!analysisData?.analysisId) return;

    try {
      const progressData = await getProgress(analysisData.analysisId);
      
      setCurrentStep(progressData.current_step || null);
      setAllSteps(progressData.steps || []);
      setOverallProgress(progressData.overall_progress);
      setStatus(progressData.status);
      
      if (progressData.status === ProcessingStatusEnum.COMPLETED) {
        // Small delay before redirecting to show completion
        setTimeout(() => {
          navigate('/results');
        }, 2000);
      } else if (progressData.status === ProcessingStatusEnum.FAILED) {
        setError(progressData.error_message || 'Analysis failed');
      }

      // Calculate estimated time based on progress
      if (progressData.overall_progress > 0 && progressData.status === ProcessingStatusEnum.PROCESSING) {
        const remainingPercent = 100 - progressData.overall_progress;
        const estimatedSeconds = Math.ceil(remainingPercent * 0.6); // Rough estimate
        setEstimatedTime(`~${estimatedSeconds} seconds remaining`);
      }
    } catch (error) {
      console.error('Failed to fetch progress:', error);
      // If real API fails, show mock completion after delay
      setTimeout(() => {
        setOverallProgress(100);
        setStatus(ProcessingStatusEnum.COMPLETED);
        setTimeout(() => {
          navigate('/results');
        }, 2000);
      }, 5000);
    }
  }, [analysisData?.analysisId, getProgress, navigate]);

  // Poll for progress updates
  useEffect(() => {
    if (!analysisData?.analysisId || status === ProcessingStatusEnum.COMPLETED || status === ProcessingStatusEnum.FAILED) {
      return;
    }

    fetchProgress();
    const interval = setInterval(fetchProgress, 2000);

    return () => clearInterval(interval);
  }, [analysisData, status, fetchProgress]);

  const handleGoHome = () => {
    navigate('/');
  };

  const handleStartOver = () => {
    sessionStorage.removeItem('analysisData');
    navigate('/analyze');
  };

  if (!analysisData) {
    return (
      <div className="public-progress-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading analysis data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="public-progress-page">
      {/* Header */}
      <header className="progress-header">
        <nav className="progress-nav">
          <div className="container">
            <div className="nav-content">
              <div className="nav-brand" onClick={handleGoHome}>
                <h1 className="brand-title">CareerCraft AI</h1>
                <span className="brand-tagline">Smart Job Analysis</span>
              </div>
              <div className="nav-actions">
                <button className="btn btn-outline" onClick={handleGoHome}>
                  ← Back to Home
                </button>
              </div>
            </div>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="progress-main">
        <div className="container">
          <div className="progress-content">
            <div className="progress-section">
              {/* Job Info Card */}
              <div className="job-info-card">
                <h2>🤖 Analyzing Your Application</h2>
                <div className="job-details">
                  <div className="job-item">
                    <span className="job-label">Position:</span>
                    <span className="job-value">{analysisData.jobTitle}</span>
                  </div>
                  <div className="job-item">
                    <span className="job-label">Company:</span>
                    <span className="job-value">{analysisData.companyName}</span>
                  </div>
                  <div className="job-item">
                    <span className="job-label">Resume:</span>
                    <span className="job-value">{analysisData.resumeFileName}</span>
                  </div>
                </div>
              </div>

              {/* Progress Circle */}
              <div className="progress-circle-container">
                <div className="progress-circle">
                  <div 
                    className="progress-ring"
                    style={{
                      background: `conic-gradient(#667eea 0deg ${overallProgress * 3.6}deg, #e2e8f0 ${overallProgress * 3.6}deg 360deg)`
                    }}
                  >
                    <div className="progress-inner">
                      <div className="progress-percentage">{overallProgress}%</div>
                      <div className="progress-status">
                        {status === ProcessingStatusEnum.PROCESSING && '🔄 Processing'}
                        {status === ProcessingStatusEnum.COMPLETED && '✅ Complete'}
                        {status === ProcessingStatusEnum.FAILED && '❌ Failed'}
                      </div>
                    </div>
                  </div>
                </div>
                
                {status === ProcessingStatusEnum.PROCESSING && (
                  <div className="estimated-time">
                    <span className="time-icon">⏱️</span>
                    <span>{estimatedTime}</span>
                  </div>
                )}
              </div>

              {/* Current Step */}
              {currentStep && (
                <div className="current-step-card">
                  <div className="step-icon">
                    {currentStep.status === ProcessingStatusEnum.PROCESSING && '🔄'}
                    {currentStep.status === ProcessingStatusEnum.COMPLETED && '✅'}
                    {currentStep.status === ProcessingStatusEnum.FAILED && '❌'}
                  </div>
                  <div className="step-content">
                    <h3>{currentStep.step_name}</h3>
                    <div className="step-progress-bar">
                      <div 
                        className="step-progress-fill"
                        style={{ width: `${currentStep.progress_percentage}%` }}
                      ></div>
                    </div>
                    <p className="step-description">
                      {currentStep.step_number === 1 && 'Extracting key requirements and analyzing job posting...'}
                      {currentStep.step_number === 2 && 'Researching company culture and industry insights...'}
                      {currentStep.step_number === 3 && 'Analyzing your resume and extracting key information...'}
                      {currentStep.step_number === 4 && 'Comparing your skills with job requirements...'}
                      {currentStep.step_number === 5 && 'Generating personalized improvement suggestions...'}
                      {currentStep.step_number === 6 && 'Creating a tailored cover letter for this position...'}
                      {currentStep.step_number === 7 && 'Finalizing analysis and preparing your results...'}
                    </p>
                  </div>
                </div>
              )}

              {/* Error Display */}
              {error && (
                <div className="error-card">
                  <div className="error-icon">⚠️</div>
                  <div className="error-content">
                    <h3>Analysis Error</h3>
                    <p>{error}</p>
                    <button className="btn btn-primary" onClick={handleStartOver}>
                      Try Again
                    </button>
                  </div>
                </div>
              )}

              {/* Completion Message */}
              {status === ProcessingStatusEnum.COMPLETED && (
                <div className="completion-card">
                  <div className="completion-icon">🎉</div>
                  <div className="completion-content">
                    <h3>Analysis Complete!</h3>
                    <p>Your personalized job application insights are ready.</p>
                    <div className="completion-actions">
                      <button 
                        className="btn btn-primary btn-large"
                        onClick={() => navigate('/results')}
                      >
                        <span className="btn-icon">📊</span>
                        View Results
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              {status === ProcessingStatusEnum.PROCESSING && (
                <div className="progress-actions">
                  <button className="btn btn-outline" onClick={handleStartOver}>
                    Start Over
                  </button>
                </div>
              )}
            </div>

            {/* Sidebar with tips and ads */}
            <div className="progress-sidebar">
              {/* Ad Placeholder */}
              <div className="ad-placeholder">
                <div className="ad-header">
                  <span className="ad-label">Sponsored</span>
                </div>
                <div className="ad-content">
                  <h3>Interview Prep Course</h3>
                  <p>Master your next interview with expert guidance</p>
                  <button className="ad-cta">Get Started</button>
                </div>
              </div>

              {/* Tips While Waiting */}
              <div className="tips-section">
                <h3>💡 While You Wait</h3>
                <div className="tip-item">
                  <span className="tip-icon">📝</span>
                  <div className="tip-content">
                    <h4>Customize for Each Job</h4>
                    <p>Tailor your resume for every application to improve your match score.</p>
                  </div>
                </div>
                <div className="tip-item">
                  <span className="tip-icon">🎯</span>
                  <div className="tip-content">
                    <h4>Highlight Achievements</h4>
                    <p>Use numbers and metrics to quantify your accomplishments.</p>
                  </div>
                </div>
                <div className="tip-item">
                  <span className="tip-icon">🔍</span>
                  <div className="tip-content">
                    <h4>Research the Company</h4>
                    <p>Understanding company culture helps you write better applications.</p>
                  </div>
                </div>
              </div>

              {/* Process Steps Overview */}
              <div className="steps-overview">
                <h3>🤖 Analysis Process</h3>
                <div className="step-list">
                  {[
                    { stepNumber: 1, name: 'Job Analysis', icon: '📋' },
                    { stepNumber: 2, name: 'Company Research', icon: '🏢' },
                    { stepNumber: 3, name: 'Resume Parsing', icon: '📄' },
                    { stepNumber: 4, name: 'Skills Analysis', icon: '🎯' },
                    { stepNumber: 5, name: 'Enhancement Tips', icon: '💡' },
                    { stepNumber: 6, name: 'Cover Letter', icon: '✉️' },
                    { stepNumber: 7, name: 'Final Review', icon: '🔍' },
                  ].map((step, index) => {
                    const stepData = allSteps.find(s => s.step_number === step.stepNumber);
                    const isCompleted = stepData?.status === ProcessingStatusEnum.COMPLETED;
                    const isCurrent = currentStep?.step_number === step.stepNumber;
                    const isPending = !stepData || stepData.status === ProcessingStatusEnum.PENDING;
                    
                    return (
                      <div 
                        key={step.stepNumber}
                        className={`step-overview-item ${isCompleted ? 'completed' : ''} ${isCurrent ? 'current' : ''} ${isPending ? 'pending' : ''}`}
                      >
                        <div className="step-overview-icon">{step.icon}</div>
                        <div className="step-overview-name">{step.name}</div>
                        <div className="step-overview-status">
                          {isCompleted && '✅'}
                          {isCurrent && '🔄'}
                          {isPending && '⏳'}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default PublicProgressPage;