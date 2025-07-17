/**
 * Public Job Analysis Page - Production workflow for job application analysis
 * Clean, public-facing interface for the job analysis service
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUpload from '../components/FileUpload';
import JobDescriptionForm from '../components/JobDescriptionForm';
import { useAnalysis } from '../contexts/AnalysisContext';
import { JobAnalysisRequest, ToneEnum } from '../types';
import './PublicAnalysisPage.css';

interface AnalysisData {
  resume?: File;
  jobDescription?: {
    jobTitle: string;
    companyName: string;
    jobDescription: string;
    jobUrl?: string;
    location?: string;
    employmentType?: string;
    experienceLevel?: string;
    salary?: string;
  };
}

interface UploadState {
  file: File | null;
  uploading: boolean;
  uploadProgress: number;
  error: string | null;
}

const PublicAnalysisPage: React.FC = () => {
  const navigate = useNavigate();
  const { startAnalysis } = useAnalysis();
  const [currentStep, setCurrentStep] = useState<'upload' | 'form' | 'review'>('upload');
  const [analysisData, setAnalysisData] = useState<AnalysisData>({});
  const [uploadState, setUploadState] = useState<UploadState>({
    file: null,
    uploading: false,
    uploadProgress: 0,
    error: null,
  });
  const [formLoading, setFormLoading] = useState(false);

  // Handle file selection
  const handleFileSelect = useCallback((file: File) => {
    setUploadState(prev => ({
      ...prev,
      file,
      error: null,
    }));
    setAnalysisData(prev => ({ ...prev, resume: file }));
  }, []);

  // Handle file removal
  const handleFileRemove = useCallback(() => {
    setUploadState({
      file: null,
      uploading: false,
      uploadProgress: 0,
      error: null,
    });
    setAnalysisData(prev => ({ ...prev, resume: undefined }));
  }, []);

  // Handle file upload
  const handleFileUpload = useCallback(async () => {
    if (!uploadState.file) return;

    setUploadState(prev => ({ ...prev, uploading: true, uploadProgress: 0, error: null }));

    try {
      // Simulate upload progress
      for (let progress = 0; progress <= 100; progress += 10) {
        await new Promise(resolve => setTimeout(resolve, 150));
        setUploadState(prev => ({ ...prev, uploadProgress: progress }));
      }

      setUploadState(prev => ({ ...prev, uploading: false }));
      setCurrentStep('form');
    } catch (error) {
      setUploadState(prev => ({
        ...prev,
        uploading: false,
        error: error instanceof Error ? error.message : 'Upload failed',
      }));
    }
  }, [uploadState.file]);

  // Handle job description form submission
  const handleJobDescriptionSubmit = useCallback((jobData: any) => {
    setAnalysisData(prev => ({ ...prev, jobDescription: jobData }));
    setCurrentStep('review');
  }, []);

  // Handle job description save
  const handleJobDescriptionSave = useCallback((jobData: any) => {
    setAnalysisData(prev => ({ ...prev, jobDescription: jobData }));
    console.log('Job description saved as draft:', jobData);
  }, []);

  // Start analysis
  const handleStartAnalysis = useCallback(async () => {
    setFormLoading(true);
    
    try {
      if (!analysisData.resume || !analysisData.jobDescription) {
        throw new Error('Resume and job description are required');
      }

      // Prepare the analysis request
      const analysisRequest: JobAnalysisRequest = {
        job_description: analysisData.jobDescription.jobDescription,
        job_url: analysisData.jobDescription.jobUrl,
        preferences: {
          tone: ToneEnum.PROFESSIONAL,
          focus_areas: ['relevant experience', 'technical skills'],
          include_salary_guidance: true,
          include_interview_prep: true
        }
      };

      console.log('Starting analysis...', analysisRequest);
      
      // Call the real API through AnalysisContext
      const sessionId = await startAnalysis(analysisRequest);
      
      // Save analysis data to session storage for progress page
      const progressData = {
        jobTitle: analysisData.jobDescription.jobTitle,
        companyName: analysisData.jobDescription.companyName,
        resumeFileName: analysisData.resume.name,
        jobDescription: analysisData.jobDescription.jobDescription,
        analysisId: sessionId,
      };
      
      sessionStorage.setItem('analysisData', JSON.stringify(progressData));
      console.log('Analysis started successfully! Session ID:', sessionId);
      
      // Navigate to progress page
      navigate('/progress');
    } catch (error) {
      console.error('Failed to start analysis:', error);
      setUploadState(prev => ({
        ...prev,
        error: 'Failed to start analysis. Please check your internet connection and try again.'
      }));
    } finally {
      setFormLoading(false);
    }
  }, [analysisData, startAnalysis, navigate]);

  // Reset workflow
  const handleReset = useCallback(() => {
    setCurrentStep('upload');
    setAnalysisData({});
    setUploadState({
      file: null,
      uploading: false,
      uploadProgress: 0,
      error: null,
    });
    setFormLoading(false);
  }, []);

  // Go back to previous step
  const handleBack = useCallback(() => {
    if (currentStep === 'form') {
      setCurrentStep('upload');
    } else if (currentStep === 'review') {
      setCurrentStep('form');
    }
  }, [currentStep]);

  const handleGoHome = () => {
    navigate('/');
  };

  return (
    <div className="public-analysis-page">
      {/* Header */}
      <header className="analysis-header">
        <nav className="analysis-nav">
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

      {/* Progress Steps */}
      <div className="analysis-progress">
        <div className="container">
          <div className="progress-header">
            <h1>AI Job Application Analysis</h1>
            <p>Get personalized insights and recommendations for your job application</p>
          </div>
          <div className="progress-steps">
            <div className={`step ${currentStep === 'upload' ? 'active' : ''} ${analysisData.resume ? 'completed' : ''}`}>
              <div className="step-number">1</div>
              <div className="step-label">Upload Resume</div>
            </div>
            <div className="step-connector"></div>
            <div className={`step ${currentStep === 'form' ? 'active' : ''} ${analysisData.jobDescription ? 'completed' : ''}`}>
              <div className="step-number">2</div>
              <div className="step-label">Job Details</div>
            </div>
            <div className="step-connector"></div>
            <div className={`step ${currentStep === 'review' ? 'active' : ''}`}>
              <div className="step-number">3</div>
              <div className="step-label">Review & Analyze</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="analysis-main">
        <div className="container">
          <div className="analysis-content">
            <div className="analysis-form">
              {/* Step 1: File Upload */}
              {currentStep === 'upload' && (
                <div className="analysis-step">
                  <div className="step-header">
                    <h2>📤 Upload Your Resume</h2>
                    <p>Upload your resume file to begin the analysis process</p>
                  </div>

                  <div className="step-content">
                    <FileUpload
                      onFileSelect={handleFileSelect}
                      onFileRemove={handleFileRemove}
                      selectedFile={uploadState.file}
                      uploading={uploadState.uploading}
                      uploadProgress={uploadState.uploadProgress}
                      error={uploadState.error}
                      disabled={uploadState.uploading}
                    />

                    {uploadState.file && !uploadState.uploading && (
                      <div className="step-actions">
                        <button
                          className="btn btn-primary btn-large"
                          onClick={handleFileUpload}
                        >
                          <span className="btn-icon">📤</span>
                          Continue to Job Details
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Step 2: Job Description Form */}
              {currentStep === 'form' && (
                <div className="analysis-step">
                  <div className="step-header">
                    <h2>📋 Job Description Details</h2>
                    <p>Provide the job information for targeted analysis</p>
                  </div>

                  <div className="step-content">
                    <JobDescriptionForm
                      onSubmit={handleJobDescriptionSubmit}
                      onSave={handleJobDescriptionSave}
                      loading={formLoading}
                      showOptionalFields={true}
                    />

                    <div className="step-navigation">
                      <button
                        className="btn btn-outline"
                        onClick={handleBack}
                        disabled={formLoading}
                      >
                        <span className="btn-icon">←</span>
                        Back to Upload
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 3: Review & Start */}
              {currentStep === 'review' && (
                <div className="analysis-step">
                  <div className="step-header">
                    <h2>🔍 Review & Start Analysis</h2>
                    <p>Review your information and start the AI analysis</p>
                  </div>

                  <div className="step-content">
                    <div className="review-section">
                      <div className="review-card">
                        <h3>📄 Resume Information</h3>
                        {analysisData.resume ? (
                          <div className="review-item">
                            <div className="item-icon">📎</div>
                            <div className="item-details">
                              <div className="item-name">{analysisData.resume.name}</div>
                              <div className="item-meta">
                                {Math.round(analysisData.resume.size / 1024)} KB • {analysisData.resume.type}
                              </div>
                            </div>
                            <button
                              className="btn-edit"
                              onClick={() => setCurrentStep('upload')}
                              disabled={formLoading}
                            >
                              Edit
                            </button>
                          </div>
                        ) : (
                          <div className="review-item-missing">
                            <span>No resume uploaded</span>
                            <button className="btn btn-outline" onClick={() => setCurrentStep('upload')}>
                              Upload Resume
                            </button>
                          </div>
                        )}
                      </div>

                      <div className="review-card">
                        <h3>🎯 Job Information</h3>
                        {analysisData.jobDescription ? (
                          <div className="job-summary">
                            <div className="summary-item">
                              <span className="summary-label">Position:</span>
                              <span className="summary-value">{analysisData.jobDescription.jobTitle}</span>
                            </div>
                            <div className="summary-item">
                              <span className="summary-label">Company:</span>
                              <span className="summary-value">{analysisData.jobDescription.companyName}</span>
                            </div>
                            {analysisData.jobDescription.location && (
                              <div className="summary-item">
                                <span className="summary-label">Location:</span>
                                <span className="summary-value">{analysisData.jobDescription.location}</span>
                              </div>
                            )}
                            {analysisData.jobDescription.employmentType && (
                              <div className="summary-item">
                                <span className="summary-label">Type:</span>
                                <span className="summary-value">{analysisData.jobDescription.employmentType}</span>
                              </div>
                            )}
                            <div className="summary-item">
                              <span className="summary-label">Description:</span>
                              <span className="summary-value">
                                {analysisData.jobDescription.jobDescription.length} characters
                              </span>
                            </div>
                            <button
                              className="btn-edit"
                              onClick={() => setCurrentStep('form')}
                              disabled={formLoading}
                            >
                              Edit
                            </button>
                          </div>
                        ) : (
                          <div className="review-item-missing">
                            <span>No job description provided</span>
                            <button className="btn btn-outline" onClick={() => setCurrentStep('form')}>
                              Add Job Details
                            </button>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="analysis-preview">
                      <h3>🤖 What You'll Get</h3>
                      <div className="preview-grid">
                        <div className="preview-item">
                          <span className="preview-icon">📊</span>
                          <span className="preview-text">Job Match Score</span>
                        </div>
                        <div className="preview-item">
                          <span className="preview-icon">🎯</span>
                          <span className="preview-text">Skills Gap Analysis</span>
                        </div>
                        <div className="preview-item">
                          <span className="preview-icon">💡</span>
                          <span className="preview-text">Resume Improvements</span>
                        </div>
                        <div className="preview-item">
                          <span className="preview-icon">✉️</span>
                          <span className="preview-text">Custom Cover Letter</span>
                        </div>
                        <div className="preview-item">
                          <span className="preview-icon">🏢</span>
                          <span className="preview-text">Company Insights</span>
                        </div>
                        <div className="preview-item">
                          <span className="preview-icon">🚀</span>
                          <span className="preview-text">Interview Tips</span>
                        </div>
                      </div>
                    </div>

                    <div className="step-actions">
                      <button
                        className="btn btn-primary btn-large"
                        onClick={handleStartAnalysis}
                        disabled={formLoading || !analysisData.resume || !analysisData.jobDescription}
                      >
                        {formLoading ? (
                          <>
                            <span className="btn-spinner">⏳</span>
                            Starting Analysis...
                          </>
                        ) : (
                          <>
                            <span className="btn-icon">🚀</span>
                            Start AI Analysis
                          </>
                        )}
                      </button>

                      <div className="action-secondary">
                        <button
                          className="btn btn-outline"
                          onClick={handleBack}
                          disabled={formLoading}
                        >
                          <span className="btn-icon">←</span>
                          Back
                        </button>

                        <button
                          className="btn btn-ghost"
                          onClick={handleReset}
                          disabled={formLoading}
                        >
                          <span className="btn-icon">🔄</span>
                          Start Over
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Sidebar with Ad */}
            <div className="analysis-sidebar">
              <div className="ad-placeholder">
                <div className="ad-header">
                  <span className="ad-label">Sponsored</span>
                </div>
                <div className="ad-content">
                  <h3>Career Coaching</h3>
                  <p>Get 1-on-1 career coaching from industry experts</p>
                  <button className="ad-cta">Learn More</button>
                </div>
              </div>

              <div className="tips-section">
                <h3>💡 Pro Tips</h3>
                <div className="tip-item">
                  <span className="tip-icon">📝</span>
                  <p>Tailor your resume keywords to match the job description</p>
                </div>
                <div className="tip-item">
                  <span className="tip-icon">🎯</span>
                  <p>Highlight quantifiable achievements and results</p>
                </div>
                <div className="tip-item">
                  <span className="tip-icon">🔍</span>
                  <p>Research the company culture and values</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default PublicAnalysisPage;