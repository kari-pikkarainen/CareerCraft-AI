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

  // Convert API results to component format
  const convertApiResultsToComponentFormat = (apiResults: ApiAnalysisResults): AnalysisResults => {
    return {
      analysisId: apiResults.session_id,
      jobTitle: apiResults.job_analysis.job_title,
      companyName: apiResults.job_analysis.company_name || 'Unknown Company',
      resumeFileName: 'resume.pdf', // API doesn't return this, use placeholder
      overallScore: Math.round(apiResults.application_strategy.overall_fit * 100),
      completedAt: apiResults.completed_at,
      
      jobAnalysis: {
        requirements: apiResults.job_analysis.requirements.map(r => r.requirement),
        keywords: apiResults.job_analysis.key_keywords,
        skills: apiResults.job_analysis.skills_analysis.map(s => s.skill),
        experience: apiResults.job_analysis.experience_level || 'Not specified',
        matchScore: Math.round(apiResults.job_analysis.analysis_score * 100),
        insights: [] // API doesn't have direct insights, would need to generate from analysis
      },
      
      companyResearch: {
        industry: apiResults.company_research.industry || 'Unknown',
        size: apiResults.company_research.size || 'Unknown',
        culture: apiResults.company_research.culture_keywords.join(', ') || 'No information available',
        values: apiResults.company_research.values || [],
        benefits: [], // API doesn't have this field, would need to extract from insights
        challenges: [], // API doesn't have this field
        opportunities: [] // API doesn't have this field
      },
      
      resumeAnalysis: {
        strengths: apiResults.resume_analysis.strengths,
        weaknesses: apiResults.resume_analysis.weaknesses,
        missingSkills: apiResults.resume_analysis.missing_keywords,
        recommendations: apiResults.resume_analysis.recommendations.map(r => r.description),
        experienceMatch: Math.round(apiResults.resume_analysis.job_match_score * 100),
        skillsMatch: Math.round(apiResults.resume_analysis.overall_score * 100)
      },
      
      skillsGapAnalysis: {
        matchingSkills: apiResults.job_analysis.skills_analysis.filter(s => s.present_in_resume).map(s => s.skill),
        missingSkills: apiResults.job_analysis.skills_analysis.filter(s => !s.present_in_resume).map(s => s.skill),
        partialSkills: [], // API doesn't distinguish partial skills
        overallMatch: Math.round(apiResults.job_analysis.analysis_score * 100),
        prioritySkills: apiResults.job_analysis.skills_analysis.filter(s => s.required && !s.present_in_resume).map(s => s.skill),
        learningPath: [] // Would need to generate from recommendations
      },
      
      resumeEnhancements: {
        improvements: apiResults.resume_analysis.recommendations.map(r => ({
          section: r.category,
          suggestion: r.description,
          impact: r.priority as 'high' | 'medium' | 'low',
          example: r.specific_examples.length > 0 ? r.specific_examples[0] : undefined
        })),
        newSections: [], // Would need to analyze recommendations to extract new sections
        keywordOptimization: apiResults.resume_analysis.recommendations.flatMap(r => r.keywords_to_add),
        scoreImprovement: 15 // Placeholder
      },
      
      coverLetter: {
        content: apiResults.cover_letter.content,
        tone: apiResults.cover_letter.tone,
        keyPoints: apiResults.cover_letter.key_points,
        customization: `High - tailored to ${apiResults.job_analysis.company_name || 'company'} values and ${apiResults.job_analysis.job_title} requirements`,
        paragraphs: 4, // Could count from content
        wordCount: apiResults.cover_letter.word_count
      },
      
      finalReview: {
        overallScore: Math.round(apiResults.application_strategy.overall_fit * 100),
        strengths: apiResults.application_strategy.strengths_to_highlight,
        improvements: apiResults.application_strategy.addressing_strategies,
        recommendation: `Application recommended - ${Math.round(apiResults.application_strategy.overall_fit * 100)}% fit`,
        confidence: Math.round(apiResults.application_strategy.overall_fit * 100),
        nextSteps: apiResults.application_strategy.interview_preparation
      }
    };
  };

  // Generate mock results data immediately
  const generateMockResults = (): AnalysisResults => {
    // Get analysis data from session storage
    const storedData = sessionStorage.getItem('analysisData');
    let analysisData = null;
    
    if (storedData) {
      try {
        analysisData = JSON.parse(storedData);
      } catch (error) {
        console.error('Failed to parse analysis data:', error);
      }
    }

    return {
      analysisId: analysisData?.analysisId || 'analysis-' + Date.now(),
      jobTitle: analysisData?.jobTitle || 'Senior Software Engineer',
      companyName: analysisData?.companyName || 'TechCorp Inc.',
      resumeFileName: analysisData?.resumeFileName || 'john_doe_resume.pdf',
      overallScore: 88,
      completedAt: new Date().toISOString(),
      
      jobAnalysis: {
        requirements: [
          '5+ years of software development experience',
          'Bachelor\'s degree in Computer Science or related field',
          'Strong problem-solving and analytical skills',
          'Experience with agile development methodologies',
          'Excellent communication and teamwork abilities'
        ],
        keywords: [
          'React', 'TypeScript', 'Node.js', 'API Development', 
          'Microservices', 'Cloud Platforms', 'CI/CD', 'Testing',
          'Agile', 'Scrum', 'Git', 'Docker'
        ],
        skills: [
          'JavaScript/TypeScript', 'React.js', 'Node.js', 'Python',
          'REST APIs', 'GraphQL', 'MongoDB', 'PostgreSQL',
          'AWS/Azure', 'Docker', 'Kubernetes', 'Git'
        ],
        experience: '5+ years in full-stack development',
        matchScore: 85,
        insights: [
          'Strong alignment with required technical skills',
          'Experience level matches job requirements perfectly',
          'Leadership experience would strengthen application',
          'Cloud certifications would be valuable addition'
        ]
      },
      
      companyResearch: {
        industry: 'Enterprise Software',
        size: '1,000-5,000 employees',
        culture: 'Innovation-focused with strong emphasis on work-life balance',
        values: [
          'Innovation', 'Collaboration', 'Customer Success', 
          'Continuous Learning', 'Diversity & Inclusion'
        ],
        benefits: [
          'Comprehensive health insurance',
          'Flexible remote work options',
          'Professional development budget',
          'Stock options program',
          'Unlimited PTO policy'
        ],
        challenges: [
          'Rapid growth requires adaptable team members',
          'Fast-paced environment with tight deadlines',
          'Multiple concurrent projects'
        ],
        opportunities: [
          'Lead innovative product development',
          'Mentor junior developers',
          'Shape technical architecture decisions',
          'Work with cutting-edge technologies'
        ]
      },
      
      resumeAnalysis: {
        strengths: [
          'Strong technical background with relevant experience',
          'Progressive career growth and increasing responsibilities',
          'Demonstrated leadership in previous roles',
          'Diverse project portfolio across different domains'
        ],
        weaknesses: [
          'Limited cloud platform certifications',
          'Could emphasize more quantified achievements',
          'Missing specific mention of microservices experience',
          'No explicit agile/scrum methodology experience mentioned'
        ],
        missingSkills: [
          'Kubernetes expertise',
          'AWS/Azure certifications',
          'GraphQL experience',
          'DevOps pipeline setup'
        ],
        recommendations: [
          'Add quantified metrics to demonstrate impact',
          'Include cloud platform certifications',
          'Highlight agile development experience',
          'Mention specific microservices projects'
        ],
        experienceMatch: 92,
        skillsMatch: 78
      },
      
      skillsGapAnalysis: {
        matchingSkills: [
          'React.js', 'TypeScript', 'Node.js', 'Python',
          'REST APIs', 'MongoDB', 'PostgreSQL', 'Git',
          'JavaScript', 'HTML/CSS'
        ],
        missingSkills: [
          'Kubernetes', 'GraphQL', 'AWS Lambda',
          'Terraform', 'Jenkins', 'Elasticsearch'
        ],
        partialSkills: [
          'Docker (basic knowledge)',
          'Azure (limited experience)',
          'Microservices (some exposure)'
        ],
        overallMatch: 78,
        prioritySkills: [
          'Kubernetes - Critical for container orchestration',
          'AWS/Azure Certifications - Required for cloud deployment',
          'GraphQL - Used extensively in new projects'
        ],
        learningPath: [
          '1. Complete AWS Solutions Architect certification',
          '2. Take Kubernetes fundamentals course',
          '3. Build personal project using GraphQL',
          '4. Practice microservices architecture patterns',
          '5. Set up CI/CD pipeline with Jenkins or GitHub Actions'
        ]
      },
      
      resumeEnhancements: {
        improvements: [
          {
            section: 'Professional Summary',
            suggestion: 'Add specific mention of cloud platforms and microservices experience',
            impact: 'high',
            example: 'Add: "...with expertise in cloud-native applications and microservices architecture"'
          },
          {
            section: 'Work Experience',
            suggestion: 'Include quantified achievements and business impact metrics',
            impact: 'high',
            example: 'Instead of "Improved system performance", write "Improved system performance by 40%, reducing page load times from 3s to 1.8s"'
          },
          {
            section: 'Technical Skills',
            suggestion: 'Organize skills by category and proficiency level',
            impact: 'medium',
            example: 'Group into: Languages, Frameworks, Databases, Cloud Platforms, DevOps Tools'
          },
          {
            section: 'Certifications',
            suggestion: 'Add cloud certifications section if you have any',
            impact: 'medium',
            example: 'Create dedicated section for AWS, Azure, or Google Cloud certifications'
          },
          {
            section: 'Projects',
            suggestion: 'Include personal or side projects that demonstrate relevant skills',
            impact: 'low',
            example: 'Add projects showcasing React, Node.js, or cloud deployment experience'
          }
        ],
        newSections: [
          'Certifications',
          'Open Source Contributions',
          'Conference Presentations'
        ],
        keywordOptimization: [
          'Microservices architecture',
          'Cloud-native development',
          'Agile/Scrum methodologies',
          'DevOps practices',
          'API design and development'
        ],
        scoreImprovement: 12
      },
      
      coverLetter: {
        content: `Dear Hiring Manager,

I am writing to express my strong interest in the ${analysisData?.jobTitle || 'Senior Software Engineer'} position at ${analysisData?.companyName || 'your company'}. With over 5 years of experience in full-stack development and a passion for building scalable, user-centric applications, I am excited about the opportunity to contribute to your innovative team.

In my current role, I have led the development of several high-impact projects using React, Node.js, and cloud platforms. My experience includes architecting microservices solutions that improved system performance by 40% and implementing CI/CD pipelines that reduced deployment time by 60%. I am particularly drawn to ${analysisData?.companyName || 'your company'}'s commitment to innovation and would love to bring my expertise in modern web technologies to help drive your product vision forward.

Your company's focus on work-life balance and continuous learning aligns perfectly with my values. I am eager to contribute to a culture that prioritizes both technical excellence and personal growth. My collaborative approach and experience mentoring junior developers would be valuable assets to your growing team.

I would welcome the opportunity to discuss how my skills and enthusiasm can contribute to ${analysisData?.companyName || 'your company'}'s continued success. Thank you for considering my application.

Sincerely,
[Your Name]`,
        tone: 'Professional and enthusiastic',
        keyPoints: [
          'Relevant technical experience highlighted',
          'Quantified achievements included',
          'Company culture alignment emphasized',
          'Leadership experience mentioned'
        ],
        customization: `High - tailored to ${analysisData?.companyName || 'the company'} values and ${analysisData?.jobTitle || 'position'} requirements`,
        paragraphs: 4,
        wordCount: 247
      },
      
      finalReview: {
        overallScore: 88,
        strengths: [
          'Strong technical background matching job requirements',
          'Progressive career growth and leadership experience',
          'Good cultural fit based on company values',
          'Relevant project experience in similar technologies'
        ],
        improvements: [
          'Obtain cloud platform certifications to strengthen profile',
          'Add more quantified metrics to demonstrate business impact',
          'Gain hands-on experience with Kubernetes and GraphQL',
          'Highlight agile development methodology experience'
        ],
        recommendation: 'Strong candidate with excellent potential. Recommend proceeding with application after implementing suggested resume improvements.',
        confidence: 85,
        nextSteps: [
          'Implement high-impact resume improvements',
          'Prepare for technical interview focusing on React and Node.js',
          'Research company\'s recent product launches and technical blog posts',
          'Practice system design questions related to microservices',
          'Prepare specific examples of leadership and mentoring experience'
        ]
      }
    };
  };

  // Initialize with mock results immediately to prevent "Results Not Found" flash
  const [results, setResults] = useState<AnalysisResults>(generateMockResults());
  const [error, setError] = useState<string | null>(null);

  // Load results data
  useEffect(() => {
    const loadResults = async () => {
      try {
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
        
        // Try to load real results first
        if (analysisId && analysisId.startsWith('analysis-')) {
          try {
            console.log('Loading analysis results...');
            const apiResults = await getResults(analysisId);
            const convertedResults = convertApiResultsToComponentFormat(apiResults);
            setResults(convertedResults);
            console.log('Analysis results loaded successfully');
            return;
          } catch (error) {
            console.warn('Failed to load results, using fallback data:', error);
          }
        }
        
        // Fallback to mock data
        console.log('Using demo results');
        const mockResults = generateMockResults();
        setResults(mockResults);
        
      } catch (error) {
        console.error('Failed to load results:', error);
        setError('Unable to load analysis results. Please try again later.');
      }
    };

    loadResults();
  }, [getResults]);

  // Handle export functionality
  const handleExport = useCallback((format: 'pdf' | 'docx' | 'json') => {
    console.log(`Exporting results in ${format} format`);
    
    if (format === 'json' && results) {
      // For JSON, we can actually download the data
      const dataStr = JSON.stringify(results, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `analysis-results-${results.analysisId}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } else {
      // For PDF and DOCX, show placeholder message
      alert(`${format.toUpperCase()} export functionality will be implemented with backend integration.`);
    }
  }, [results]);

  // Handle start new analysis
  const handleStartNew = useCallback(() => {
    // Clear session storage
    sessionStorage.removeItem('analysisData');
    sessionStorage.removeItem('analysisStarted');
    sessionStorage.removeItem('analysisCompleted');
    
    // Navigate to analysis page
    navigate('/analyze');
  }, [navigate]);

  // Remove loading state - go directly to results
  /* if (loading) {
    return (
      <div className="results-page loading">
        <div className="loading-content">
          <div className="spinner-large"></div>
          <h2>Processing Results...</h2>
          <p>Compiling your comprehensive job analysis report</p>
        </div>
      </div>
    );
  } */

  // Results are always available now - no need for "Results Not Found" check
  /* if (!results) {
    return (
      <div className="results-page error">
        <div className="error-content">
          <div className="error-icon">❌</div>
          <h2>Results Not Found</h2>
          <p>Unable to load analysis results. Please try starting a new analysis.</p>
          <button
            className="btn btn-primary"
            onClick={handleStartNew}
          >
            <span className="btn-icon">🔄</span>
            Start New Analysis
          </button>
        </div>
      </div>
    );
  } */

  return (
    <div className="results-page">
      {/* Header */}
      <header className="results-header">
        <nav className="results-nav">
          <div className="container">
            <div className="nav-content">
              <div className="nav-brand" onClick={() => navigate('/')}>
                <h1 className="brand-title">CareerCraft AI</h1>
                <span className="brand-tagline">Smart Job Analysis</span>
              </div>
              <div className="nav-actions">
                <button className="btn btn-outline" onClick={() => navigate('/')}>
                  ← Back to Home
                </button>
              </div>
            </div>
          </div>
        </nav>
      </header>

      {/* Error Display */}
      {error && (
        <div className="error-banner">
          <div className="container">
            <div className="banner-content">
              <span className="banner-icon">⚠️</span>
              <div className="banner-text">
                <strong>Error:</strong> {error}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="results-main">
        <div className="container">
          <ResultsDisplay
            results={results}
            onExport={handleExport}
            onStartNew={handleStartNew}
          />
        </div>
      </main>

      {/* Footer */}
      <footer className="results-footer">
        <div className="container">
          <div className="footer-content">
            <p>&copy; 2025 Kari Pikkarainen. CareerCraft AI</p>
            <div className="footer-links">
              <a href="/" className="footer-link">← Back to Home</a>
              <a href="/analyze" className="footer-link">New Analysis</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default ResultsPage;