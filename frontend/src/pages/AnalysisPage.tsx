/**
 * Job Analysis Page - Complete workflow for job application analysis
 * Integrates file upload and job description input for comprehensive analysis
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2024 Kari Pikkarainen. All rights reserved.
 */

import React, { useState, useCallback } from 'react';
import FileUpload from '../components/FileUpload';
import JobDescriptionForm from '../components/JobDescriptionForm';
import { useAnalysis } from '../contexts/AnalysisContext';
import { JobAnalysisRequest, ToneEnum } from '../types';
import './AnalysisPage.css';

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

const AnalysisPage: React.FC = () => {
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
        await new Promise(resolve => setTimeout(resolve, 200));
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

      console.log('🚀 Starting real analysis with API...', analysisRequest);
      
      // Call the real API through AnalysisContext
      const sessionId = await startAnalysis(analysisRequest);
      
      // Save analysis data to session storage for progress page
      const progressData = {
        jobTitle: analysisData.jobDescription.jobTitle,
        companyName: analysisData.jobDescription.companyName,
        resumeFileName: analysisData.resume.name,
        jobDescription: analysisData.jobDescription.jobDescription,
        analysisId: sessionId, // Use real session ID from API
      };
      
      sessionStorage.setItem('analysisData', JSON.stringify(progressData));
      console.log('✅ Real analysis started successfully! Session ID:', sessionId);
      
      // Navigate to progress page
      window.location.href = '/local/progress';
    } catch (error) {
      console.error('❌ Failed to start analysis:', error);
      // Still navigate to show the error or fallback behavior
      if (analysisData.resume && analysisData.jobDescription) {
        const fallbackData = {
          jobTitle: analysisData.jobDescription.jobTitle,
          companyName: analysisData.jobDescription.companyName,
          resumeFileName: analysisData.resume.name,
          jobDescription: analysisData.jobDescription.jobDescription,
          analysisId: 'mock-analysis-' + Date.now(), // Mock ID for fallback
        };
        sessionStorage.setItem('analysisData', JSON.stringify(fallbackData));
        console.log('⚠️ Using fallback mock analysis mode');
        window.location.href = '/local/progress';
      }
    } finally {
      setFormLoading(false);
    }
  }, [analysisData, startAnalysis]);

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

  return (
    <div className="analysis-page">
      {/* Header */}
      <header className="analysis-header">
        <div className="container">
          <div className="header-content">
            <div className="breadcrumb">
              <a href="/local" className="breadcrumb-link">🧪 Local Development</a>
              <span className="breadcrumb-separator">›</span>
              <span className="breadcrumb-current">🎯 Job Analysis</span>
            </div>
            <h1>AI-Powered Job Application Analysis</h1>
            <p className="page-description">
              Upload your resume and provide job details for comprehensive analysis and recommendations
            </p>
          </div>
        </div>
      </header>

      {/* Progress Steps */}
      <div className="analysis-progress">
        <div className="container">
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
              <div className="step-label">Review & Start</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="analysis-main">
        <div className="container">
          {/* Step 1: File Upload */}
          {currentStep === 'upload' && (
            <div className="analysis-step">
              <div className="step-header">
                <h2>📤 Step 1: Upload Your Resume</h2>
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
                      className="btn btn-primary"
                      onClick={handleFileUpload}
                    >
                      <span className="btn-icon">📤</span>
                      Upload & Continue
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
                <h2>📋 Step 2: Job Description Details</h2>
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
                <h2>🔍 Step 3: Review & Start Analysis</h2>
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

                <div className="analysis-info">
                  <h3>🤖 Analysis Process</h3>
                  <div className="process-steps">
                    <div className="process-step">
                      <span className="process-icon">📋</span>
                      <span className="process-text">Job Description Analysis</span>
                    </div>
                    <div className="process-step">
                      <span className="process-icon">🏢</span>
                      <span className="process-text">Company Research</span>
                    </div>
                    <div className="process-step">
                      <span className="process-icon">📄</span>
                      <span className="process-text">Resume Analysis</span>
                    </div>
                    <div className="process-step">
                      <span className="process-icon">🔍</span>
                      <span className="process-text">Skills Gap Analysis</span>
                    </div>
                    <div className="process-step">
                      <span className="process-icon">💡</span>
                      <span className="process-text">Recommendations</span>
                    </div>
                    <div className="process-step">
                      <span className="process-icon">✉️</span>
                      <span className="process-text">Cover Letter Generation</span>
                    </div>
                  </div>
                </div>

                <div className="step-actions">
                  <button
                    className="btn btn-primary"
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

                  <button
                    className="btn btn-outline"
                    onClick={handleBack}
                    disabled={formLoading}
                  >
                    <span className="btn-icon">←</span>
                    Back to Job Details
                  </button>

                  <button
                    className="btn btn-secondary"
                    onClick={handleReset}
                    disabled={formLoading}
                  >
                    <span className="btn-icon">🔄</span>
                    Start Over
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="analysis-footer">
        <div className="container">
          <div className="footer-content">
            <p>&copy; 2024 Kari Pikkarainen. CareerCraft AI - Local Development</p>
            <div className="footer-links">
              <a href="/local" className="footer-link">← Back to Development</a>
              <a href="/local/upload" className="footer-link">File Upload Test</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default AnalysisPage;