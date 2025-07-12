/**
 * CareerCraft AI - Public Home Page
 * A production-ready landing page for the job analysis service
 * 
 * Copyright (c) 2024 Kari Pikkarainen. All rights reserved.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate('/analyze');
  };

  return (
    <div className="home-page">
      {/* Header */}
      <header className="main-header">
        <nav className="navbar">
          <div className="container">
            <div className="nav-brand">
              <h1 className="brand-title">CareerCraft AI</h1>
              <span className="brand-tagline">Smart Job Analysis</span>
            </div>
            <div className="nav-links">
              <a href="#features" className="nav-link">Features</a>
              <a href="#how-it-works" className="nav-link">How it Works</a>
              <button className="btn btn-primary" onClick={handleGetStarted}>
                Get Started Free
              </button>
            </div>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="container">
          <div className="hero-content">
            <div className="hero-text">
              <h1 className="hero-title">
                AI-Powered Job Application Analysis
              </h1>
              <p className="hero-subtitle">
                Upload your resume and get instant, personalized recommendations 
                to land your dream job. Our AI analyzes job requirements, identifies 
                skill gaps, and creates tailored cover letters.
              </p>
              <div className="hero-actions">
                <button className="btn btn-primary btn-large" onClick={handleGetStarted}>
                  <span className="btn-icon">🚀</span>
                  Start Free Analysis
                </button>
                <div className="hero-features">
                  <div className="feature-badge">
                    <span className="badge-icon">⚡</span>
                    <span>Instant Results</span>
                  </div>
                  <div className="feature-badge">
                    <span className="badge-icon">🔒</span>
                    <span>Secure & Private</span>
                  </div>
                  <div className="feature-badge">
                    <span className="badge-icon">🆓</span>
                    <span>No Registration</span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Ad Placeholder */}
            <div className="hero-ad">
              <div className="ad-placeholder">
                <div className="ad-header">
                  <span className="ad-label">Advertisement</span>
                </div>
                <div className="ad-content">
                  <h3>Career Boost Platform</h3>
                  <p>Advanced job search tools and career coaching</p>
                  <button className="ad-cta">Learn More</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features-section">
        <div className="container">
          <div className="section-header">
            <h2>Powerful AI Analysis Tools</h2>
            <p>Everything you need to optimize your job applications</p>
          </div>
          
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">📋</div>
              <h3>Smart Job Analysis</h3>
              <p>AI extracts key requirements, skills, and qualifications from any job posting</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🎯</div>
              <h3>Skills Gap Detection</h3>
              <p>Identify missing skills and get recommendations for improvement</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">📄</div>
              <h3>Resume Optimization</h3>
              <p>Get specific suggestions to improve your resume for each position</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">✉️</div>
              <h3>Custom Cover Letters</h3>
              <p>AI generates personalized cover letters tailored to the job and company</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🏢</div>
              <h3>Company Research</h3>
              <p>Learn about company culture, values, and recent developments</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Match Scoring</h3>
              <p>See how well your profile matches the job requirements</p>
            </div>
          </div>
        </div>
      </section>

      {/* Ad Section */}
      <section className="ad-section">
        <div className="container">
          <div className="ad-banner">
            <div className="ad-placeholder ad-large">
              <div className="ad-header">
                <span className="ad-label">Sponsored</span>
              </div>
              <div className="ad-content">
                <h3>Professional Resume Writing Service</h3>
                <p>Get your resume professionally written by industry experts. 30% off this month!</p>
                <button className="ad-cta">Claim Discount</button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="how-it-works-section">
        <div className="container">
          <div className="section-header">
            <h2>How It Works</h2>
            <p>Get professional insights in just 3 simple steps</p>
          </div>
          
          <div className="steps-grid">
            <div className="step-card">
              <div className="step-number">1</div>
              <div className="step-content">
                <h3>Upload Your Resume</h3>
                <p>Securely upload your resume in PDF, Word, or text format</p>
                <div className="step-icon">📤</div>
              </div>
            </div>
            
            <div className="step-arrow">→</div>
            
            <div className="step-card">
              <div className="step-number">2</div>
              <div className="step-content">
                <h3>Add Job Details</h3>
                <p>Paste the job description or provide key job information</p>
                <div className="step-icon">📋</div>
              </div>
            </div>
            
            <div className="step-arrow">→</div>
            
            <div className="step-card">
              <div className="step-number">3</div>
              <div className="step-content">
                <h3>Get AI Analysis</h3>
                <p>Receive comprehensive analysis and personalized recommendations</p>
                <div className="step-icon">🤖</div>
              </div>
            </div>
          </div>
          
          <div className="cta-section">
            <button className="btn btn-primary btn-large" onClick={handleGetStarted}>
              <span className="btn-icon">🚀</span>
              Start Your Analysis Now
            </button>
            <p className="cta-subtitle">Free • No registration required • Results in minutes</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="main-footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-brand">
              <h3>CareerCraft AI</h3>
              <p>Empowering job seekers with AI-driven insights</p>
            </div>
            
            <div className="footer-links">
              <div className="link-group">
                <h4>Product</h4>
                <a href="#features">Features</a>
                <a href="#how-it-works">How it Works</a>
                <a href="/analyze">Start Analysis</a>
              </div>
              
              <div className="link-group">
                <h4>Support</h4>
                <a href="#faq">FAQ</a>
                <a href="#contact">Contact</a>
                <a href="#help">Help Center</a>
              </div>
              
              <div className="link-group">
                <h4>Legal</h4>
                <a href="#privacy">Privacy Policy</a>
                <a href="#terms">Terms of Service</a>
                <a href="#cookies">Cookie Policy</a>
              </div>
            </div>
          </div>
          
          <div className="footer-bottom">
            <p>&copy; 2024 Kari Pikkarainen. CareerCraft AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;