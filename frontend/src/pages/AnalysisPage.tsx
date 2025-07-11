import React from 'react';

const AnalysisPage: React.FC = () => {
  return (
    <div className="analysis-page">
      <div className="page-header">
        <h1>🎯 New Job Analysis</h1>
        <p>Upload your resume and job description to get AI-powered insights</p>
      </div>
      
      <div className="page-content">
        <div className="placeholder-card">
          <h2>Coming Soon</h2>
          <p>This page will contain:</p>
          <ul>
            <li>File upload component for resumes</li>
            <li>Job description input form</li>
            <li>Analysis preferences settings</li>
            <li>Real-time progress tracking</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default AnalysisPage;