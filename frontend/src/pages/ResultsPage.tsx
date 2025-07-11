import React from 'react';
import { useParams } from 'react-router-dom';

const ResultsPage: React.FC = () => {
  const { analysisId } = useParams<{ analysisId: string }>();

  return (
    <div className="results-page">
      <div className="page-header">
        <h1>📊 Analysis Results</h1>
        <p>Analysis ID: {analysisId}</p>
      </div>
      
      <div className="page-content">
        <div className="placeholder-card">
          <h2>Coming Soon</h2>
          <p>This page will display:</p>
          <ul>
            <li>Job analysis summary</li>
            <li>Resume recommendations</li>
            <li>Generated cover letter</li>
            <li>Skills gap analysis</li>
            <li>Company research insights</li>
            <li>Download and export options</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;