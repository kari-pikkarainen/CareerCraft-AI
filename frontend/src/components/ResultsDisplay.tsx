/**
 * Results Display Component
 * Comprehensive display of job analysis results
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

import React, { useState, useCallback } from 'react';
import './ResultsDisplay.css';

export interface AnalysisResults {
  analysisId: string;
  jobTitle: string;
  companyName: string;
  resumeFileName: string;
  overallScore: number;
  completedAt: string;
  
  // Step results
  jobAnalysis: {
    requirements: string[];
    keywords: string[];
    skills: string[];
    experience: string;
    matchScore: number;
    insights: string[];
  };
  
  companyResearch: {
    industry: string;
    size: string;
    culture: string;
    values: string[];
    benefits: string[];
    challenges: string[];
    opportunities: string[];
  };
  
  resumeAnalysis: {
    strengths: string[];
    weaknesses: string[];
    missingSkills: string[];
    recommendations: string[];
    experienceMatch: number;
    skillsMatch: number;
  };
  
  skillsGapAnalysis: {
    matchingSkills: string[];
    missingSkills: string[];
    partialSkills: string[];
    overallMatch: number;
    prioritySkills: string[];
    learningPath: string[];
  };
  
  resumeEnhancements: {
    improvements: Array<{
      section: string;
      suggestion: string;
      impact: 'high' | 'medium' | 'low';
      example?: string;
    }>;
    newSections: string[];
    keywordOptimization: string[];
    scoreImprovement: number;
  };
  
  coverLetter: {
    content: string;
    tone: string;
    keyPoints: string[];
    customization: string;
    paragraphs: number;
    wordCount: number;
  };
  
  finalReview: {
    overallScore: number;
    strengths: string[];
    improvements: string[];
    recommendation: string;
    confidence: number;
    nextSteps: string[];
  };
}

interface ResultsDisplayProps {
  results: AnalysisResults;
  onExport?: (format: 'pdf' | 'docx' | 'json') => void;
  onStartNew?: () => void;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({
  results,
  onExport,
  onStartNew,
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'detailed' | 'cover-letter' | 'export'>('overview');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  // Toggle section expansion
  const toggleSection = useCallback((sectionId: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId);
      } else {
        newSet.add(sectionId);
      }
      return newSet;
    });
  }, []);

  // Get score color based on percentage
  const getScoreColor = useCallback((score: number): string => {
    if (score >= 85) return 'excellent';
    if (score >= 70) return 'good';
    if (score >= 50) return 'fair';
    return 'poor';
  }, []);

  // Format date
  const formatDate = useCallback((dateString: string): string => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }, []);

  return (
    <div className="results-display">
      {/* Header Summary */}
      <div className="results-header">
        <div className="analysis-meta">
          <h1>📊 Analysis Results</h1>
          <div className="meta-info">
            <div className="meta-item">
              <span className="meta-label">Position:</span>
              <span className="meta-value">{results.jobTitle}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Company:</span>
              <span className="meta-value">{results.companyName}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Resume:</span>
              <span className="meta-value">{results.resumeFileName}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Completed:</span>
              <span className="meta-value">{formatDate(results.completedAt)}</span>
            </div>
          </div>
        </div>
        
        <div className="overall-score">
          <div className={`score-circle ${getScoreColor(results.overallScore)}`}>
            <span className="score-number">{results.overallScore}</span>
            <span className="score-label">Overall Score</span>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="results-tabs">
        <button
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <span className="tab-icon">📋</span>
          Overview
        </button>
        <button
          className={`tab ${activeTab === 'detailed' ? 'active' : ''}`}
          onClick={() => setActiveTab('detailed')}
        >
          <span className="tab-icon">🔍</span>
          Detailed Analysis
        </button>
        <button
          className={`tab ${activeTab === 'cover-letter' ? 'active' : ''}`}
          onClick={() => setActiveTab('cover-letter')}
        >
          <span className="tab-icon">✉️</span>
          Cover Letter
        </button>
        <button
          className={`tab ${activeTab === 'export' ? 'active' : ''}`}
          onClick={() => setActiveTab('export')}
        >
          <span className="tab-icon">📤</span>
          Export
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="overview-content">
            {/* Key Metrics */}
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-icon">🎯</div>
                <div className="metric-info">
                  <div className="metric-value">{results.jobAnalysis.matchScore}%</div>
                  <div className="metric-label">Job Match</div>
                </div>
              </div>
              
              <div className="metric-card">
                <div className="metric-icon">💼</div>
                <div className="metric-info">
                  <div className="metric-value">{results.resumeAnalysis.experienceMatch}%</div>
                  <div className="metric-label">Experience Match</div>
                </div>
              </div>
              
              <div className="metric-card">
                <div className="metric-icon">🛠️</div>
                <div className="metric-info">
                  <div className="metric-value">{results.skillsGapAnalysis.overallMatch}%</div>
                  <div className="metric-label">Skills Match</div>
                </div>
              </div>
              
              <div className="metric-card">
                <div className="metric-icon">✨</div>
                <div className="metric-info">
                  <div className="metric-value">+{results.resumeEnhancements.scoreImprovement}</div>
                  <div className="metric-label">Potential Improvement</div>
                </div>
              </div>
            </div>

            {/* Quick Insights */}
            <div className="insights-section">
              <h2>🎯 Key Insights</h2>
              
              <div className="insight-cards">
                <div className="insight-card strengths">
                  <h3>💪 Top Strengths</h3>
                  <ul>
                    {results.finalReview.strengths.slice(0, 3).map((strength, index) => (
                      <li key={index}>{strength}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="insight-card improvements">
                  <h3>🚀 Priority Improvements</h3>
                  <ul>
                    {results.resumeEnhancements.improvements
                      .filter(imp => imp.impact === 'high')
                      .slice(0, 3)
                      .map((improvement, index) => (
                        <li key={index}>
                          <strong>{improvement.section}:</strong> {improvement.suggestion}
                        </li>
                      ))}
                  </ul>
                </div>
                
                <div className="insight-card missing-skills">
                  <h3>📚 Skills to Develop</h3>
                  <ul>
                    {results.skillsGapAnalysis.prioritySkills.slice(0, 3).map((skill, index) => (
                      <li key={index}>{skill}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* Recommendation */}
            <div className="recommendation-section">
              <h2>💡 Final Recommendation</h2>
              <div className="recommendation-card">
                <div className="recommendation-header">
                  <div className={`confidence-badge ${results.finalReview.confidence >= 80 ? 'high' : results.finalReview.confidence >= 60 ? 'medium' : 'low'}`}>
                    {results.finalReview.confidence}% Confidence
                  </div>
                </div>
                <p className="recommendation-text">{results.finalReview.recommendation}</p>
                
                <div className="next-steps">
                  <h4>📋 Recommended Next Steps:</h4>
                  <ol>
                    {results.finalReview.nextSteps.map((step, index) => (
                      <li key={index}>{step}</li>
                    ))}
                  </ol>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Detailed Analysis Tab */}
        {activeTab === 'detailed' && (
          <div className="detailed-content">
            {/* Job Analysis Section */}
            <div className="analysis-section">
              <div 
                className="section-header"
                onClick={() => toggleSection('job-analysis')}
              >
                <h2>📋 Job Description Analysis</h2>
                <button className="expand-btn">
                  {expandedSections.has('job-analysis') ? '−' : '+'}
                </button>
              </div>
              
              {expandedSections.has('job-analysis') && (
                <div className="section-content">
                  <div className="analysis-grid">
                    <div className="analysis-item">
                      <h4>Required Skills ({results.jobAnalysis.skills.length})</h4>
                      <div className="tag-list">
                        {results.jobAnalysis.skills.map((skill, index) => (
                          <span key={index} className="tag skill-tag">{skill}</span>
                        ))}
                      </div>
                    </div>
                    
                    <div className="analysis-item">
                      <h4>Key Requirements</h4>
                      <ul>
                        {results.jobAnalysis.requirements.map((req, index) => (
                          <li key={index}>{req}</li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="analysis-item">
                      <h4>Important Keywords</h4>
                      <div className="tag-list">
                        {results.jobAnalysis.keywords.map((keyword, index) => (
                          <span key={index} className="tag keyword-tag">{keyword}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Company Research Section */}
            <div className="analysis-section">
              <div 
                className="section-header"
                onClick={() => toggleSection('company-research')}
              >
                <h2>🏢 Company Research</h2>
                <button className="expand-btn">
                  {expandedSections.has('company-research') ? '−' : '+'}
                </button>
              </div>
              
              {expandedSections.has('company-research') && (
                <div className="section-content">
                  <div className="company-grid">
                    <div className="company-info">
                      <h4>Company Profile</h4>
                      <div className="info-grid">
                        <div className="info-item">
                          <span className="info-label">Industry:</span>
                          <span className="info-value">{results.companyResearch.industry}</span>
                        </div>
                        <div className="info-item">
                          <span className="info-label">Size:</span>
                          <span className="info-value">{results.companyResearch.size}</span>
                        </div>
                        <div className="info-item">
                          <span className="info-label">Culture:</span>
                          <span className="info-value">{results.companyResearch.culture}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="company-insights">
                      <div className="insight-group">
                        <h4>🎯 Company Values</h4>
                        <div className="tag-list">
                          {results.companyResearch.values.map((value, index) => (
                            <span key={index} className="tag value-tag">{value}</span>
                          ))}
                        </div>
                      </div>
                      
                      <div className="insight-group">
                        <h4>💰 Benefits & Perks</h4>
                        <ul>
                          {results.companyResearch.benefits.map((benefit, index) => (
                            <li key={index}>{benefit}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Skills Gap Analysis Section */}
            <div className="analysis-section">
              <div 
                className="section-header"
                onClick={() => toggleSection('skills-gap')}
              >
                <h2>🔍 Skills Gap Analysis</h2>
                <button className="expand-btn">
                  {expandedSections.has('skills-gap') ? '−' : '+'}
                </button>
              </div>
              
              {expandedSections.has('skills-gap') && (
                <div className="section-content">
                  <div className="skills-breakdown">
                    <div className="skills-group matching">
                      <h4>✅ Matching Skills ({results.skillsGapAnalysis.matchingSkills.length})</h4>
                      <div className="tag-list">
                        {results.skillsGapAnalysis.matchingSkills.map((skill, index) => (
                          <span key={index} className="tag matching-skill">{skill}</span>
                        ))}
                      </div>
                    </div>
                    
                    <div className="skills-group missing">
                      <h4>❌ Missing Skills ({results.skillsGapAnalysis.missingSkills.length})</h4>
                      <div className="tag-list">
                        {results.skillsGapAnalysis.missingSkills.map((skill, index) => (
                          <span key={index} className="tag missing-skill">{skill}</span>
                        ))}
                      </div>
                    </div>
                    
                    <div className="skills-group learning">
                      <h4>📚 Recommended Learning Path</h4>
                      <ol className="learning-path">
                        {results.skillsGapAnalysis.learningPath.map((item, index) => (
                          <li key={index}>{item}</li>
                        ))}
                      </ol>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Resume Enhancements Section */}
            <div className="analysis-section">
              <div 
                className="section-header"
                onClick={() => toggleSection('enhancements')}
              >
                <h2>💡 Resume Enhancement Recommendations</h2>
                <button className="expand-btn">
                  {expandedSections.has('enhancements') ? '−' : '+'}
                </button>
              </div>
              
              {expandedSections.has('enhancements') && (
                <div className="section-content">
                  <div className="enhancements-list">
                    {results.resumeEnhancements.improvements.map((improvement, index) => (
                      <div key={index} className={`enhancement-item ${improvement.impact}`}>
                        <div className="enhancement-header">
                          <span className={`impact-badge ${improvement.impact}`}>
                            {improvement.impact.toUpperCase()}
                          </span>
                          <h4>{improvement.section}</h4>
                        </div>
                        <p className="enhancement-suggestion">{improvement.suggestion}</p>
                        {improvement.example && (
                          <div className="enhancement-example">
                            <strong>Example:</strong> {improvement.example}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Cover Letter Tab */}
        {activeTab === 'cover-letter' && (
          <div className="cover-letter-content">
            <div className="cover-letter-header">
              <h2>✉️ Generated Cover Letter</h2>
              <div className="letter-meta">
                <div className="meta-item">
                  <span className="meta-label">Tone:</span>
                  <span className="meta-value">{results.coverLetter.tone}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Length:</span>
                  <span className="meta-value">{results.coverLetter.wordCount} words</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Customization:</span>
                  <span className="meta-value">{results.coverLetter.customization}</span>
                </div>
              </div>
            </div>
            
            <div className="cover-letter-body">
              <div className="letter-content">
                {results.coverLetter.content.split('\n\n').map((paragraph, index) => (
                  <p key={index} className="letter-paragraph">{paragraph}</p>
                ))}
              </div>
              
              <div className="letter-sidebar">
                <div className="key-points">
                  <h4>🎯 Key Points Highlighted</h4>
                  <ul>
                    {results.coverLetter.keyPoints.map((point, index) => (
                      <li key={index}>{point}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="letter-actions">
                  <button className="btn btn-primary">
                    <span className="btn-icon">📝</span>
                    Edit Letter
                  </button>
                  <button className="btn btn-outline">
                    <span className="btn-icon">📋</span>
                    Copy to Clipboard
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Export Tab */}
        {activeTab === 'export' && (
          <div className="export-content">
            <h2>📤 Export Results</h2>
            
            <div className="export-options">
              <div className="export-section">
                <h3>📄 Document Formats</h3>
                <div className="export-grid">
                  <button
                    className="export-option"
                    onClick={() => onExport?.('pdf')}
                  >
                    <div className="export-icon">📕</div>
                    <div className="export-info">
                      <h4>PDF Report</h4>
                      <p>Complete analysis with formatting</p>
                    </div>
                  </button>
                  
                  <button
                    className="export-option"
                    onClick={() => onExport?.('docx')}
                  >
                    <div className="export-icon">📘</div>
                    <div className="export-info">
                      <h4>Word Document</h4>
                      <p>Editable document format</p>
                    </div>
                  </button>
                  
                  <button
                    className="export-option"
                    onClick={() => onExport?.('json')}
                  >
                    <div className="export-icon">🗃️</div>
                    <div className="export-info">
                      <h4>JSON Data</h4>
                      <p>Raw data for developers</p>
                    </div>
                  </button>
                </div>
              </div>
              
              <div className="export-section">
                <h3>📊 Individual Components</h3>
                <div className="component-exports">
                  <label className="export-checkbox">
                    <input type="checkbox" defaultChecked />
                    <span>Job Analysis Summary</span>
                  </label>
                  <label className="export-checkbox">
                    <input type="checkbox" defaultChecked />
                    <span>Resume Recommendations</span>
                  </label>
                  <label className="export-checkbox">
                    <input type="checkbox" defaultChecked />
                    <span>Cover Letter</span>
                  </label>
                  <label className="export-checkbox">
                    <input type="checkbox" defaultChecked />
                    <span>Skills Gap Analysis</span>
                  </label>
                  <label className="export-checkbox">
                    <input type="checkbox" />
                    <span>Company Research</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Action Footer */}
      <div className="results-footer">
        <div className="footer-actions">
          <button
            className="btn btn-outline"
            onClick={onStartNew}
          >
            <span className="btn-icon">🔄</span>
            Start New Analysis
          </button>
          
          <button className="btn btn-secondary">
            <span className="btn-icon">💾</span>
            Save Results
          </button>
          
          <button className="btn btn-primary">
            <span className="btn-icon">📤</span>
            Export All
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResultsDisplay;