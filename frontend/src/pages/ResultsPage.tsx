/**
 * Results Page - Display comprehensive job analysis results
 * Shows detailed analysis, recommendations, and cover letter
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import ResultsDisplay, { AnalysisResults } from '../components/ResultsDisplay';
import { useAnalysis } from '../contexts/AnalysisContext';
import './ResultsPage.css';

const ResultsPage: React.FC = () => {
  const navigate = useNavigate();
  const { getResults } = useAnalysis();
  const getResultsRef = useRef(getResults);
  
  // Update ref when getResults changes
  getResultsRef.current = getResults;

  // Convert API results to component format (simplified version with error handling)
  const convertApiResultsToComponentFormat = (apiResults: any): AnalysisResults => {
    console.log('Converting API results - starting validation...');
    
    // Validate required properties
    if (!apiResults.session_id) {
      throw new Error('Missing session_id in API response');
    }
    
    if (!apiResults.job_analysis) {
      throw new Error('Missing job_analysis in API response');
    }
    
    if (!apiResults.final_summary && !apiResults.application_strategy) {
      console.warn('⚠️ Missing both final_summary and application_strategy in API response - using fallback');
      // Don't throw error, use fallback instead
    }
    
    // Log the validation check
    console.log('✓ All required properties present');
    
    // Log structure for debugging
    console.log('📋 job_analysis structure:', apiResults.job_analysis);
    console.log('📋 final_summary structure:', apiResults.final_summary);
    console.log('📋 parsed_resume structure:', apiResults.parsed_resume);
    
    return {
      analysisId: apiResults.session_id,
      jobTitle: apiResults.job_analysis?.job_summary?.title || apiResults.final_summary?.key_findings?.job_title || 'Unknown Position',
      companyName: apiResults.job_analysis?.job_summary?.company || apiResults.final_summary?.key_findings?.company || 'Unknown Company',
      resumeFileName: 'resume.pdf',
      overallScore: Math.round((apiResults.final_summary?.job_match_score || 0) * 100),
      completedAt: apiResults.completed_at || new Date().toISOString(),
      
      jobAnalysis: {
        requirements: [
          ...(apiResults.job_analysis?.key_requirements?.technical_skills || []),
          ...(apiResults.job_analysis?.responsibilities?.primary_duties || [])
        ],
        keywords: [
          ...(apiResults.job_analysis?.keywords_ats?.technical || []),
          ...(apiResults.job_analysis?.keywords_ats?.soft_skills || [])
        ],
        skills: apiResults.job_analysis?.key_requirements?.technical_skills || [],
        experience: apiResults.job_analysis?.job_summary?.experience_level || 'Not specified',
        matchScore: Math.round((apiResults.final_summary?.job_match_score || 0) * 100),
        insights: []
      },
      
      companyResearch: {
        industry: apiResults.company_research?.industry || 'Technology',
        size: apiResults.company_research?.size || 'Large Enterprise',
        culture: (apiResults.company_research?.culture_insights || []).join(', ') || `${apiResults.job_analysis?.job_summary?.company || 'Company'} - Technology company focused on innovation and collaboration`,
        values: ['Innovation', 'Technology Excellence', 'Customer Focus'],
        benefits: apiResults.job_analysis?.compensation ? [`Salary: ${apiResults.job_analysis.compensation.base_salary_range}`, 'Bonus', 'Equity', 'Benefits package'] : [],
        challenges: [],
        opportunities: []
      },
      
      resumeAnalysis: {
        strengths: apiResults.resume_recommendations?.skills_analysis?.skills_present || [],
        weaknesses: apiResults.resume_recommendations?.experience_alignment?.improvements_needed || [],
        missingSkills: apiResults.resume_recommendations?.skills_analysis?.recommended_additions || [],
        recommendations: apiResults.resume_recommendations?.resume_structure?.formatting_recommendations || [],
        experienceMatch: Math.round((apiResults.final_summary?.job_match_score || 0) * 100),
        skillsMatch: Math.round((apiResults.final_summary?.job_match_score || 0) * 100)
      },
      
      skillsGapAnalysis: {
        matchingSkills: apiResults.skills_analysis?.skillsInventory?.present || [],
        missingSkills: apiResults.skills_analysis?.gapAnalysis?.criticalMissing || [],
        partialSkills: apiResults.skills_analysis?.gapAnalysis?.needsStrengthening || [],
        overallMatch: Math.round((apiResults.final_summary?.job_match_score || 0) * 100),
        prioritySkills: (apiResults.skills_analysis?.gapAnalysis?.criticalMissing || []).slice(0, 5),
        learningPath: apiResults.skills_analysis?.learningPriorities?.immediate || []
      },
      
      resumeEnhancements: {
        improvements: (apiResults.resume_recommendations?.experience_alignment?.improvements_needed || []).map((improvement: string) => ({
          section: 'Experience',
          suggestion: improvement,
          impact: 'high' as const
        })),
        newSections: apiResults.resume_recommendations?.resume_structure?.missing_sections || [],
        keywordOptimization: apiResults.resume_recommendations?.skills_analysis?.recommended_additions || [],
        scoreImprovement: Math.round((apiResults.final_summary?.job_match_score || 0) * 100)
      },
      
      coverLetter: {
        content: apiResults.cover_letter?.content || '',
        tone: apiResults.cover_letter?.tone || 'professional',
        keyPoints: apiResults.cover_letter?.key_points || [],
        customization: 'Generated based on job requirements',
        paragraphs: 3,
        wordCount: apiResults.cover_letter?.word_count || 0
      },
      
      finalReview: {
        overallScore: Math.round((apiResults.final_summary?.job_match_score || 0) * 100),
        strengths: Object.values(apiResults.resume_recommendations?.skills_analysis?.skills_present || []),
        improvements: apiResults.resume_recommendations?.experience_alignment?.improvements_needed || [],
        recommendation: `${apiResults.final_summary?.recommendations_summary?.application_strength || 'No assessment available'}. Match score: ${Math.round((apiResults.final_summary?.job_match_score || 0) * 100)}%`,
        confidence: Math.round((apiResults.final_summary?.job_match_score || 0) * 100),
        nextSteps: apiResults.final_summary?.next_steps || []
      }
    };
  };


  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Load results data - run only once on mount
  useEffect(() => {
    console.log('ResultsPage: Loading results (useEffect triggered)');
    
    const loadResults = async () => {
      try {
        setLoading(true);
        setError(null);

        // Check if we have a real analysis session ID
        let analysisId = null;
        
        // First try URL parameter
        const urlParams = new URLSearchParams(window.location.search);
        const urlAnalysisId = urlParams.get('analysis');
        if (urlAnalysisId) {
          analysisId = urlAnalysisId;
          console.log('Analysis ID from URL:', analysisId);
        }
        
        // Fallback to session storage
        if (!analysisId) {
          const storedData = sessionStorage.getItem('analysisData');
          console.log('Stored analysis data:', storedData);
          
          if (storedData) {
            try {
              const parsedData = JSON.parse(storedData);
              analysisId = parsedData.analysisId;
              console.log('Parsed analysis ID from session storage:', analysisId);
            } catch (error) {
              console.error('Failed to parse stored analysis data:', error);
            }
          } else {
            console.log('No analysis data found in session storage');
          }
        }
        
        // Try to load real results
        if (analysisId && analysisId.startsWith('analysis_')) {
          try {
            console.log('Loading analysis results for ID:', analysisId);
            console.log('Calling getResults API...');
            
            // Add a small delay to ensure backend has finished writing results
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            const apiResults = await getResultsRef.current(analysisId);
            console.log('API Results received:', apiResults);
            console.log('API Results type:', typeof apiResults);
            console.log('API Results keys:', apiResults ? Object.keys(apiResults) : 'no keys');
            
            if (!apiResults) {
              console.error('API returned null/undefined results');
              setError('No analysis results returned from server.');
              return;
            }
            
            try {
              console.log('Starting conversion of API results...');
              console.log('Expected properties check:');
              console.log('- session_id:', apiResults.session_id);
              console.log('- job_analysis:', !!apiResults.job_analysis);
              console.log('- company_research:', !!apiResults.company_research);
              console.log('- resume_analysis:', !!apiResults.resume_analysis);
            console.log('- parsed_resume:', !!apiResults.parsed_resume);
              console.log('- application_strategy:', !!apiResults.application_strategy);
            console.log('- final_summary:', !!apiResults.final_summary);
              console.log('- completed_at:', apiResults.completed_at);
              
              console.log('🔍 ALL available properties in API response:', Object.keys(apiResults));
              
              if (apiResults.job_analysis) {
                console.log('job_analysis keys:', Object.keys(apiResults.job_analysis));
              }
              
              const convertedResults = convertApiResultsToComponentFormat(apiResults);
              console.log('Converted results:', convertedResults);
              
              if (!convertedResults) {
                console.error('Conversion returned null/undefined');
                setError('Failed to process analysis results.');
                return;
              }
              
              console.log('Setting results state...');
              setResults(convertedResults);
              console.log('Analysis results loaded successfully');
              setLoading(false);
              return;
            } catch (conversionError) {
              console.error('Error during results conversion:', conversionError);
              setError('Failed to process analysis results format.');
              return;
            }
          } catch (error) {
            console.error('Failed to load results - Full error:', error);
            console.error('Error type:', typeof error);
            console.error('Error message:', error instanceof Error ? error.message : 'Unknown error');
            console.error('Error stack:', error instanceof Error ? error.stack : 'No stack available');
            
            // Handle rate limiting gracefully
            if (error instanceof Error && error.message.includes('429')) {
              console.log('Rate limit hit while loading results');
              setError('Server is busy. Please wait a moment and refresh the page.');
              return;
            }
            
            setError('Unable to load analysis results. The analysis may still be processing or the session may have expired.');
          }
        } else {
          console.log('Analysis ID validation failed:');
          console.log('- analysisId:', analysisId);
          console.log('- analysisId type:', typeof analysisId);
          console.log('- analysisId length:', analysisId ? analysisId.length : 'null/undefined');
          console.log('- starts with analysis_:', analysisId ? analysisId.startsWith('analysis_') : 'cannot check');
          setError('No valid analysis session found. Please start a new analysis.');
        }
        
      } catch (error) {
        console.error('Failed to load results:', error);
        
        // Handle rate limiting gracefully
        if (error instanceof Error && error.message.includes('429')) {
          console.log('Rate limit hit while loading results');
          setError('Server is busy. Please wait a moment and refresh the page.');
        } else {
          setError('Unable to load analysis results. Please try again later.');
        }
      } finally {
        setLoading(false);
      }
    };

    loadResults();
  }, []); // Empty dependency array - only run once on mount

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
        {/* Header */}
        <header className="analysis-header">
          <nav className="analysis-nav">
            <div className="container">
              <div className="nav-content">
                <div className="nav-brand" onClick={handleBackToHome}>
                  <h1 className="brand-title">CareerCraft AI</h1>
                  <span className="brand-tagline">Smart Job Analysis</span>
                </div>
                <div className="nav-actions">
                  <button onClick={handleBackToHome} className="btn btn-outline">
                    ← Back to Home
                  </button>
                </div>
              </div>
            </div>
          </nav>
        </header>

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
        {/* Header */}
        <header className="analysis-header">
          <nav className="analysis-nav">
            <div className="container">
              <div className="nav-content">
                <div className="nav-brand" onClick={handleBackToHome}>
                  <h1 className="brand-title">CareerCraft AI</h1>
                  <span className="brand-tagline">Smart Job Analysis</span>
                </div>
                <div className="nav-actions">
                  <button onClick={handleBackToHome} className="btn btn-outline">
                    ← Back to Home
                  </button>
                </div>
              </div>
            </div>
          </nav>
        </header>

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
      {/* Header */}
      <header className="analysis-header">
        <nav className="analysis-nav">
          <div className="container">
            <div className="nav-content">
              <div className="nav-brand" onClick={handleBackToHome}>
                <h1 className="brand-title">CareerCraft AI</h1>
                <span className="brand-tagline">Smart Job Analysis</span>
              </div>
              <div className="nav-actions">
                <button onClick={handleStartNewAnalysis} className="btn btn-primary">
                  🚀 New Analysis
                </button>
                <button onClick={handleBackToHome} className="btn btn-outline">
                  ← Back to Home
                </button>
              </div>
            </div>
          </div>
        </nav>
      </header>

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