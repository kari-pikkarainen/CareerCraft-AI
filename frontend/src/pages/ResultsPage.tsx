/**
 * Results Page - Display comprehensive job analysis results
 * Shows detailed analysis, recommendations, and cover letter
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import ResultsDisplay, { AnalysisResults } from '../components/ResultsDisplay';
import { useAnalysis } from '../contexts/AnalysisContext';
import { AnalysisResults as ApiAnalysisResults } from '../types';
import './ResultsPage.css';

const ResultsPage: React.FC = () => {
  const navigate = useNavigate();
  const { getResults } = useAnalysis();

  // Convert API results to component format (simplified version)
  const convertApiResultsToComponentFormat = (apiResults: ApiAnalysisResults): AnalysisResults => {
    return {
      analysisId: apiResults.session_id,
      jobTitle: apiResults.job_analysis.job_title,
      companyName: apiResults.job_analysis.company_name || 'Unknown Company',
      resumeFileName: 'resume.pdf',
      overallScore: Math.round(apiResults.application_strategy.overall_fit * 100),
      completedAt: apiResults.completed_at,
      
      jobAnalysis: {
        requirements: apiResults.job_analysis.requirements.map((req: any) => 
          typeof req === 'string' ? req : req.requirement || req.description || req.toString()
        ),
        keywords: apiResults.job_analysis.key_keywords || [],
        skills: apiResults.job_analysis.key_keywords || [],
        experience: apiResults.job_analysis.experience_level || 'Not specified',
        matchScore: Math.round((apiResults.job_analysis.analysis_score || 0) * 100),
        insights: []
      },
      
      companyResearch: {
        industry: apiResults.company_research.industry || 'Unknown',
        size: apiResults.company_research.size || 'Unknown',
        culture: apiResults.company_research.culture_keywords.join(', ') || 'No information available',
        values: apiResults.company_research.values || [],
        benefits: [],
        challenges: [],
        opportunities: []
      },
      
      resumeAnalysis: {
        strengths: apiResults.resume_analysis.strengths || [],
        weaknesses: apiResults.resume_analysis.weaknesses || [],
        missingSkills: apiResults.resume_analysis.missing_keywords || [],
        recommendations: apiResults.resume_analysis.recommendations?.map((rec: any) => 
          typeof rec === 'string' ? rec : rec.description || rec.title || rec.toString()
        ) || [],
        experienceMatch: Math.round((apiResults.resume_analysis.overall_score || 0) * 100),
        skillsMatch: Math.round((apiResults.resume_analysis.job_match_score || 0) * 100)
      },
      
      skillsGapAnalysis: {
        matchingSkills: apiResults.resume_analysis.strengths || [],
        missingSkills: apiResults.resume_analysis.missing_keywords || [],
        partialSkills: [],
        overallMatch: Math.round((apiResults.resume_analysis.job_match_score || 0) * 100),
        prioritySkills: apiResults.resume_analysis.missing_keywords?.slice(0, 5) || [],
        learningPath: []
      },
      
      resumeEnhancements: {
        improvements: [{
          section: 'General',
          suggestion: 'Review resume analysis for detailed recommendations',
          impact: 'high' as const
        }],
        newSections: [],
        keywordOptimization: apiResults.resume_analysis.missing_keywords || [],
        scoreImprovement: Math.round((apiResults.resume_analysis.job_match_score || 0) * 100)
      },
      
      coverLetter: {
        content: apiResults.cover_letter.content || '',
        tone: apiResults.cover_letter.tone || 'professional',
        keyPoints: apiResults.cover_letter.key_points || [],
        customization: 'Generated based on job requirements',
        paragraphs: 3,
        wordCount: apiResults.cover_letter.word_count || 0
      },
      
      applicationStrategy: {
        timeline: Object.entries(apiResults.application_strategy.timeline_recommendations || {}).map(
          ([key, value]) => `${key}: ${value}`
        ),
        interviewPrep: apiResults.application_strategy.interview_preparation || [],
        followUp: apiResults.application_strategy.addressing_strategies || [],
        tips: apiResults.application_strategy.strengths_to_highlight || []
      }
    };
  };

  const getAnalysisDataFromSession = () => {
    const storedData = sessionStorage.getItem('analysisData');
    if (storedData) {
      try {
        return JSON.parse(storedData);
      } catch (error) {
        console.error('Failed to parse analysis data:', error);
      }
    }
    return null;
  };

  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Load results data
  useEffect(() => {
    const loadResults = async () => {
      try {
        setLoading(true);
        setError(null);

        // Check if we have a real analysis session ID
        const storedData = sessionStorage.getItem('analysisData');
        let analysisId = null;
        
        if (storedData) {
          try {
            const parsedData = JSON.parse(storedData);
            analysisId = parsedData.analysisId;
          } catch (error) {
            console.error('Failed to parse stored analysis data:', error);
          }
        }
        
        // Try to load real results
        if (analysisId && analysisId.startsWith('analysis-')) {
          try {
            console.log('Loading analysis results...');
            const apiResults = await getResults(analysisId);
            const convertedResults = convertApiResultsToComponentFormat(apiResults);
            setResults(convertedResults);
            console.log('Analysis results loaded successfully');
            setLoading(false);
            return;
          } catch (error) {
            console.warn('Failed to load results:', error);
            setError('Unable to load analysis results. The analysis may still be processing or the session may have expired.');
          }
        } else {
          setError('No valid analysis session found. Please start a new analysis.');
        }
        
      } catch (error) {
        console.error('Failed to load results:', error);
        setError('Unable to load analysis results. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    loadResults();
  }, [getResults]);

  const handleStartNewAnalysis = useCallback(() => {
    // Clear any stored data
    sessionStorage.removeItem('analysisData');
    navigate('/analyze');
  }, [navigate]);

  const handleBackToHome = useCallback(() => {
    navigate('/');
  }, [navigate]);

  // Loading state
  if (loading) {
    return (
      <div className="results-page">
        <div className="results-header">
          <div className="header-content">
            <h1>📊 Analysis Results</h1>
            <div className="header-actions">
              <button onClick={handleBackToHome} className="btn btn-outline">
                ← Back to Home
              </button>
            </div>
          </div>
        </div>

        <div className="results-content">
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <h2>Loading Analysis Results...</h2>
            <p>Please wait while we retrieve your job analysis results.</p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !results) {
    return (
      <div className="results-page">
        <div className="results-header">
          <div className="header-content">
            <h1>📊 Analysis Results</h1>
            <div className="header-actions">
              <button onClick={handleBackToHome} className="btn btn-outline">
                ← Back to Home
              </button>
            </div>
          </div>
        </div>

        <div className="results-content">
          <div className="error-state">
            <div className="error-icon">⚠️</div>
            <h2>Results Not Available</h2>
            <p>{error || 'No analysis results found.'}</p>
            <div className="error-actions">
              <button onClick={handleStartNewAnalysis} className="btn btn-primary">
                🚀 Start New Analysis
              </button>
              <button onClick={handleBackToHome} className="btn btn-outline">
                ← Back to Home
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Results display
  return (
    <div className="results-page">
      <div className="results-header">
        <div className="header-content">
          <h1>📊 Analysis Results</h1>
          <div className="header-actions">
            <button onClick={handleStartNewAnalysis} className="btn btn-primary">
              🚀 New Analysis
            </button>
            <button onClick={handleBackToHome} className="btn btn-outline">
              ← Back to Home
            </button>
          </div>
        </div>
      </div>

      <div className="results-content">
        <ResultsDisplay results={results} />
        
        <div className="export-section">
          <h3>📄 Export Options</h3>
          <p>Export functionality (PDF/DOCX) will be available in a future update.</p>
          <div className="export-actions">
            <button className="btn btn-outline" disabled>
              📄 Export as PDF
            </button>
            <button className="btn btn-outline" disabled>
              📝 Export as DOCX
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;