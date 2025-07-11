import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useAnalysis } from '../contexts/AnalysisContext';
import './DashboardPage.css';

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const { analysisHistory } = useAnalysis();

  const recentAnalyses = analysisHistory.slice(0, 3);

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h1>Welcome back{user?.email ? `, ${user.email.split('@')[0]}` : ''}!</h1>
        <p>Ready to craft your next career opportunity?</p>
      </div>

      <div className="dashboard-grid">
        {/* Quick Actions */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2>🚀 Quick Actions</h2>
          </div>
          <div className="card-body">
            <div className="action-buttons">
              <Link to="/analyze" className="btn btn-primary btn-lg">
                <span className="btn-icon">🎯</span>
                Start New Analysis
              </Link>
              <Link to="/history" className="btn btn-secondary">
                <span className="btn-icon">📋</span>
                View History
              </Link>
            </div>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2>📊 Your Stats</h2>
          </div>
          <div className="card-body">
            <div className="stats-grid">
              <div className="stat-item">
                <div className="stat-value">{analysisHistory.length}</div>
                <div className="stat-label">Total Analyses</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">
                  {analysisHistory.filter(a => a.status === 'completed').length}
                </div>
                <div className="stat-label">Completed</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">0</div>
                <div className="stat-label">Cover Letters</div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="dashboard-card full-width">
          <div className="card-header">
            <h2>🕒 Recent Activity</h2>
            {analysisHistory.length > 3 && (
              <Link to="/history" className="view-all-link">
                View All
              </Link>
            )}
          </div>
          <div className="card-body">
            {recentAnalyses.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📭</div>
                <h3>No analyses yet</h3>
                <p>Start your first job analysis to see your activity here.</p>
                <Link to="/analyze" className="btn btn-primary">
                  Get Started
                </Link>
              </div>
            ) : (
              <div className="activity-list">
                {recentAnalyses.map((analysis) => (
                  <div key={analysis.analysis_id} className="activity-item">
                    <div className="activity-info">
                      <h4>{analysis.job_description_preview}</h4>
                      <p className="activity-meta">
                        {new Date(analysis.started_at).toLocaleDateString()} • 
                        <span className={`status status-${analysis.status}`}>
                          {analysis.status}
                        </span>
                      </p>
                    </div>
                    <div className="activity-progress">
                      <div className="progress-bar">
                        <div 
                          className="progress-fill"
                          style={{ width: `${analysis.overall_progress}%` }}
                        />
                      </div>
                      <span className="progress-text">
                        {analysis.overall_progress}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Getting Started Guide */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2>🎓 Getting Started</h2>
          </div>
          <div className="card-body">
            <div className="guide-steps">
              <div className="guide-step">
                <div className="step-number">1</div>
                <div className="step-content">
                  <h4>Upload Resume</h4>
                  <p>Upload your resume in PDF, DOCX, or TXT format</p>
                </div>
              </div>
              <div className="guide-step">
                <div className="step-number">2</div>
                <div className="step-content">
                  <h4>Add Job Description</h4>
                  <p>Paste the job posting you're interested in</p>
                </div>
              </div>
              <div className="guide-step">
                <div className="step-number">3</div>
                <div className="step-content">
                  <h4>Get AI Analysis</h4>
                  <p>Receive personalized recommendations and cover letter</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Tips & Insights */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2>💡 Pro Tips</h2>
          </div>
          <div className="card-body">
            <div className="tips-list">
              <div className="tip-item">
                <span className="tip-icon">🎯</span>
                <p>Use specific job titles for better matching</p>
              </div>
              <div className="tip-item">
                <span className="tip-icon">📝</span>
                <p>Include complete job requirements for detailed analysis</p>
              </div>
              <div className="tip-item">
                <span className="tip-icon">🚀</span>
                <p>Update your resume regularly with new skills</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;