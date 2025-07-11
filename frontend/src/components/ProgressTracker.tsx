/**
 * Progress Tracker Component
 * Real-time progress tracking for 7-step job analysis workflow
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2024 Kari Pikkarainen. All rights reserved.
 */

import React, { useState, useEffect, useCallback } from 'react';
import './ProgressTracker.css';

export interface WorkflowStep {
  id: string;
  name: string;
  description: string;
  percentage: number;
  icon: string;
  estimatedTime: number; // in seconds
}

export interface ProgressState {
  currentStep: number;
  currentPercentage: number;
  stepStatus: 'pending' | 'running' | 'completed' | 'failed';
  startTime?: Date;
  estimatedEndTime?: Date;
  stepStartTime?: Date;
  error?: string;
  details?: string;
}

interface ProgressTrackerProps {
  isActive: boolean;
  onComplete: () => void;
  onError: (error: string) => void;
  simulateProgress?: boolean; // For local testing
  analysisData?: {
    jobTitle: string;
    companyName: string;
    resumeFileName: string;
  };
}

const WORKFLOW_STEPS: WorkflowStep[] = [
  {
    id: 'job_analysis',
    name: 'Job Description Analysis',
    description: 'Extracting requirements, skills, and keywords from job posting',
    percentage: 14,
    icon: '📋',
    estimatedTime: 45,
  },
  {
    id: 'company_research',
    name: 'Company Research',
    description: 'Researching company culture, values, and insights',
    percentage: 28,
    icon: '🏢',
    estimatedTime: 60,
  },
  {
    id: 'resume_parsing',
    name: 'Resume Analysis',
    description: 'Parsing and structuring resume content',
    percentage: 42,
    icon: '📄',
    estimatedTime: 30,
  },
  {
    id: 'skills_analysis',
    name: 'Skills Gap Analysis',
    description: 'Comparing resume skills vs job requirements',
    percentage: 57,
    icon: '🔍',
    estimatedTime: 40,
  },
  {
    id: 'resume_enhancement',
    name: 'Resume Enhancement',
    description: 'Generating improvement recommendations',
    percentage: 71,
    icon: '💡',
    estimatedTime: 50,
  },
  {
    id: 'cover_letter',
    name: 'Cover Letter Generation',
    description: 'Creating personalized cover letter',
    percentage: 85,
    icon: '✉️',
    estimatedTime: 35,
  },
  {
    id: 'final_review',
    name: 'Final Review & Formatting',
    description: 'Quality check, scoring, and final summary',
    percentage: 100,
    icon: '✅',
    estimatedTime: 20,
  },
];

const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  isActive,
  onComplete,
  onError,
  simulateProgress = true,
  analysisData,
}) => {
  const [progress, setProgress] = useState<ProgressState>({
    currentStep: 0,
    currentPercentage: 0,
    stepStatus: 'pending',
  });

  const [stepResults, setStepResults] = useState<Record<string, any>>({});

  // Calculate total estimated time
  const totalEstimatedTime = WORKFLOW_STEPS.reduce((sum, step) => sum + step.estimatedTime, 0);

  // Format time for display
  const formatTime = useCallback((seconds: number): string => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return remainingSeconds > 0 ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
  }, []);

  // Calculate estimated end time
  const calculateEstimatedEndTime = useCallback((startTime: Date, currentStep: number): Date => {
    const remainingTime = WORKFLOW_STEPS
      .slice(currentStep)
      .reduce((sum, step) => sum + step.estimatedTime, 0);
    return new Date(startTime.getTime() + remainingTime * 1000);
  }, []);

  // Generate mock data for each step
  const generateMockStepData = useCallback((stepId: string) => {
    switch (stepId) {
      case 'job_analysis':
        return {
          keywords: ['Python', 'React', 'TypeScript', 'API Development'],
          requirements: ['3+ years experience', 'Bachelor\'s degree', 'Team collaboration'],
          matchScore: 85,
        };
      case 'company_research':
        return {
          industry: 'Technology',
          size: '1000-5000 employees',
          culture: 'Innovation-focused, collaborative environment',
          benefits: ['Health insurance', 'Remote work', 'Learning budget'],
        };
      case 'resume_parsing':
        return {
          sections: ['Contact', 'Experience', 'Education', 'Skills'],
          experience: '4 years',
          skills: ['JavaScript', 'Python', 'React', 'Node.js'],
          education: 'Bachelor of Science in Computer Science',
        };
      case 'skills_analysis':
        return {
          matchingSkills: ['Python', 'React', 'API Development'],
          missingSkills: ['Docker', 'AWS'],
          overallMatch: 78,
          recommendations: ['Consider highlighting Docker experience', 'Add cloud platforms to skills'],
        };
      case 'resume_enhancement':
        return {
          improvements: [
            'Add quantified achievements in current role',
            'Include relevant certifications',
            'Optimize keywords for ATS systems',
          ],
          score: 82,
        };
      case 'cover_letter':
        return {
          paragraphs: 4,
          tone: 'Professional and enthusiastic',
          customization: 'High - tailored to company and role',
          keyPoints: ['Relevant experience', 'Cultural fit', 'Specific achievements'],
        };
      case 'final_review':
        return {
          overallScore: 88,
          strengths: ['Strong technical background', 'Relevant experience', 'Good cultural fit'],
          improvements: ['Add cloud experience', 'Include team leadership examples'],
          recommendation: 'Strong candidate - proceed with application',
        };
      default:
        return {};
    }
  }, []);

  // Simulate step progress for local testing
  const simulateStepProgress = useCallback(async (stepIndex: number): Promise<void> => {
    const step = WORKFLOW_STEPS[stepIndex];
    const stepStartTime = new Date();
    
    setProgress(prev => ({
      ...prev,
      currentStep: stepIndex,
      stepStatus: 'running',
      stepStartTime,
      details: step.description,
    }));

    // Simulate gradual progress within the step
    const progressIncrement = (step.percentage - (stepIndex > 0 ? WORKFLOW_STEPS[stepIndex - 1].percentage : 0)) / 10;
    const basePercentage = stepIndex > 0 ? WORKFLOW_STEPS[stepIndex - 1].percentage : 0;

    for (let i = 0; i <= 10; i++) {
      await new Promise(resolve => setTimeout(resolve, (step.estimatedTime * 1000) / 10));
      
      const currentPercentage = Math.min(basePercentage + (progressIncrement * i), step.percentage);
      
      setProgress(prev => ({
        ...prev,
        currentPercentage,
        details: i < 5 ? step.description : `Completing ${step.name.toLowerCase()}...`,
      }));
    }

    // Simulate step result
    const stepResult = {
      stepId: step.id,
      status: 'completed',
      duration: step.estimatedTime,
      result: `${step.name} completed successfully`,
      data: generateMockStepData(step.id),
    };

    setStepResults(prev => ({ ...prev, [step.id]: stepResult }));

    setProgress(prev => ({
      ...prev,
      stepStatus: 'completed',
      currentPercentage: step.percentage,
    }));

    // Small delay before next step
    await new Promise(resolve => setTimeout(resolve, 500));
  }, [generateMockStepData]);

  // Start progress simulation
  const startProgress = useCallback(async () => {
    if (!isActive || !simulateProgress) return;

    const startTime = new Date();
    const estimatedEndTime = calculateEstimatedEndTime(startTime, 0);

    setProgress({
      currentStep: 0,
      currentPercentage: 0,
      stepStatus: 'running',
      startTime,
      estimatedEndTime,
    });

    try {
      for (let i = 0; i < WORKFLOW_STEPS.length; i++) {
        await simulateStepProgress(i);
      }

      // Mark as completed
      setProgress(prev => ({
        ...prev,
        stepStatus: 'completed',
        currentPercentage: 100,
        details: 'Analysis completed successfully!',
      }));

      setTimeout(() => {
        onComplete();
      }, 1000);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Analysis failed';
      setProgress(prev => ({
        ...prev,
        stepStatus: 'failed',
        error: errorMessage,
      }));
      onError(errorMessage);
    }
  }, [isActive, simulateProgress, calculateEstimatedEndTime, simulateStepProgress, onComplete, onError]);

  // Start progress when component becomes active
  useEffect(() => {
    if (isActive && simulateProgress) {
      startProgress();
    }
  }, [isActive, simulateProgress, startProgress]);

  // Get current step info
  const currentStepInfo = progress.currentStep < WORKFLOW_STEPS.length ? WORKFLOW_STEPS[progress.currentStep] : null;
  const isCompleted = progress.stepStatus === 'completed' && progress.currentPercentage === 100;
  const isFailed = progress.stepStatus === 'failed';

  return (
    <div className="progress-tracker">
      {/* Header */}
      <div className="progress-header">
        <div className="progress-title">
          <h2>🤖 AI Analysis in Progress</h2>
          {analysisData && (
            <div className="analysis-info">
              <span className="info-item">
                <strong>Position:</strong> {analysisData.jobTitle}
              </span>
              <span className="info-item">
                <strong>Company:</strong> {analysisData.companyName}
              </span>
              <span className="info-item">
                <strong>Resume:</strong> {analysisData.resumeFileName}
              </span>
            </div>
          )}
        </div>
        
        <div className="progress-stats">
          <div className="stat-item">
            <span className="stat-value">{progress.currentPercentage}%</span>
            <span className="stat-label">Complete</span>
          </div>
          {progress.estimatedEndTime && !isCompleted && (
            <div className="stat-item">
              <span className="stat-value">
                {formatTime(Math.max(0, Math.floor((progress.estimatedEndTime.getTime() - Date.now()) / 1000)))}
              </span>
              <span className="stat-label">Remaining</span>
            </div>
          )}
          <div className="stat-item">
            <span className="stat-value">{formatTime(totalEstimatedTime)}</span>
            <span className="stat-label">Total Time</span>
          </div>
        </div>
      </div>

      {/* Overall Progress Bar */}
      <div className="overall-progress">
        <div className="progress-bar">
          <div 
            className={`progress-fill ${isFailed ? 'error' : isCompleted ? 'complete' : 'active'}`}
            style={{ width: `${progress.currentPercentage}%` }}
          />
        </div>
        <div className="progress-percentage">{progress.currentPercentage}%</div>
      </div>

      {/* Current Step Info */}
      {currentStepInfo && !isCompleted && !isFailed && (
        <div className="current-step">
          <div className="step-icon">{currentStepInfo.icon}</div>
          <div className="step-info">
            <h3>{currentStepInfo.name}</h3>
            <p>{progress.details || currentStepInfo.description}</p>
          </div>
          <div className="step-loader">
            <div className="spinner"></div>
          </div>
        </div>
      )}

      {/* Error State */}
      {isFailed && (
        <div className="error-state">
          <div className="error-icon">❌</div>
          <div className="error-content">
            <h3>Analysis Failed</h3>
            <p>{progress.error || 'An unexpected error occurred during analysis.'}</p>
          </div>
        </div>
      )}

      {/* Success State */}
      {isCompleted && (
        <div className="success-state">
          <div className="success-icon">🎉</div>
          <div className="success-content">
            <h3>Analysis Complete!</h3>
            <p>Your job application analysis has been completed successfully.</p>
          </div>
        </div>
      )}

      {/* Steps List */}
      <div className="steps-list">
        {WORKFLOW_STEPS.map((step, index) => {
          const isCurrentStep = index === progress.currentStep && !isCompleted;
          const isCompletedStep = index < progress.currentStep || isCompleted;
          const stepResult = stepResults[step.id];

          return (
            <div
              key={step.id}
              className={`step-item ${isCurrentStep ? 'current' : ''} ${isCompletedStep ? 'completed' : ''}`}
            >
              <div className="step-marker">
                <div className="step-number">
                  {isCompletedStep ? '✓' : index + 1}
                </div>
              </div>
              
              <div className="step-content">
                <div className="step-header">
                  <span className="step-icon">{step.icon}</span>
                  <h4>{step.name}</h4>
                  <span className="step-percentage">{step.percentage}%</span>
                </div>
                
                <p className="step-description">{step.description}</p>
                
                {stepResult && (
                  <div className="step-result">
                    <div className="result-summary">
                      {step.id === 'job_analysis' && stepResult.data && (
                        <div className="result-items">
                          <span>Keywords: {stepResult.data.keywords?.slice(0, 3).join(', ')}</span>
                          <span>Match: {stepResult.data.matchScore}%</span>
                        </div>
                      )}
                      {step.id === 'skills_analysis' && stepResult.data && (
                        <div className="result-items">
                          <span>Overall Match: {stepResult.data.overallMatch}%</span>
                          <span>Missing: {stepResult.data.missingSkills?.length || 0} skills</span>
                        </div>
                      )}
                      {step.id === 'final_review' && stepResult.data && (
                        <div className="result-items">
                          <span>Score: {stepResult.data.overallScore}%</span>
                          <span>{stepResult.data.recommendation}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
                
                <div className="step-timing">
                  <span className="estimated-time">~{formatTime(step.estimatedTime)}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ProgressTracker;