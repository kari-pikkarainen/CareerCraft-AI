/**
 * CareerCraft AI - Intelligent Job Application Assistant
 * Copyright (c) 2024 Kari Pikkarainen. All rights reserved.
 * 
 * This software is proprietary and confidential.
 * Unauthorized use, distribution, or modification is strictly prohibited.
 */

import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Initialize services
import { initializeServices, checkServiceHealth } from './services';

// Import pages (we'll create these next)
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import AnalysisPage from './pages/AnalysisPage';
import ResultsPage from './pages/ResultsPage';
import HistoryPage from './pages/HistoryPage';
import ProfilePage from './pages/ProfilePage';

// Import components
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';

// Import context providers
import { AuthProvider } from './contexts/AuthContext';
import { AnalysisProvider } from './contexts/AnalysisContext';

const App: React.FC = () => {
  const [servicesInitialized, setServicesInitialized] = useState(false);
  const [initializationError, setInitializationError] = useState<string | null>(null);

  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Initialize all services
        initializeServices();
        
        // Check service health
        const health = await checkServiceHealth();
        if (!health.overall) {
          console.warn('Some services are not healthy:', health);
        }
        
        setServicesInitialized(true);
      } catch (error) {
        console.error('Failed to initialize application:', error);
        setInitializationError(error instanceof Error ? error.message : 'Initialization failed');
      }
    };

    initializeApp();
  }, []);

  // Show loading or error during initialization
  if (!servicesInitialized) {
    if (initializationError) {
      return (
        <div className="app-error">
          <h1>Application Error</h1>
          <p>Failed to initialize services: {initializationError}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      );
    }
    
    return (
      <div className="app-loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
        <p>Initializing CareerCraft AI...</p>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <AuthProvider>
        <AnalysisProvider>
          <Router>
            <div className="App">
              <Routes>
                {/* Public routes */}
                <Route path="/login" element={<LoginPage />} />
                
                {/* Protected routes with layout */}
                <Route path="/" element={
                  <ProtectedRoute>
                    <Layout />
                  </ProtectedRoute>
                }>
                  {/* Dashboard - main landing page */}
                  <Route index element={<DashboardPage />} />
                  
                  {/* Analysis workflow */}
                  <Route path="analyze" element={<AnalysisPage />} />
                  <Route path="analysis/:analysisId/results" element={<ResultsPage />} />
                  
                  {/* History and profile */}
                  <Route path="history" element={<HistoryPage />} />
                  <Route path="profile" element={<ProfilePage />} />
                </Route>
                
                {/* Catch all - redirect to dashboard */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </div>
          </Router>
        </AnalysisProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default App;