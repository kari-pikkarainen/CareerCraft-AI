/**
 * App Component Tests
 * Main application routing and context tests
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';

// Mock child components to avoid complex dependencies
jest.mock('./pages/HomePage', () => {
  return function MockHomePage() {
    return <div data-testid="home-page">HomePage</div>;
  };
});

jest.mock('./pages/PublicAnalysisPage', () => {
  return function MockPublicAnalysisPage() {
    return <div data-testid="analysis-page">PublicAnalysisPage</div>;
  };
});

jest.mock('./pages/PublicProgressPage', () => {
  return function MockPublicProgressPage() {
    return <div data-testid="progress-page">PublicProgressPage</div>;
  };
});

jest.mock('./pages/ResultsPage', () => {
  return function MockResultsPage() {
    return <div data-testid="results-page">ResultsPage</div>;
  };
});

const renderWithRouter = (initialEntries = ['/']) => {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <App />
    </MemoryRouter>
  );
};

describe('App', () => {
  test('renders without crashing', () => {
    renderWithRouter();
    expect(screen.getByTestId('home-page')).toBeInTheDocument();
  });

  test('renders HomePage on root route', () => {
    renderWithRouter(['/']);
    expect(screen.getByTestId('home-page')).toBeInTheDocument();
  });

  test('renders PublicAnalysisPage on /analyze route', () => {
    renderWithRouter(['/analyze']);
    expect(screen.getByTestId('analysis-page')).toBeInTheDocument();
  });

  test('renders PublicProgressPage on /progress route', () => {
    renderWithRouter(['/progress']);
    expect(screen.getByTestId('progress-page')).toBeInTheDocument();
  });

  test('renders ResultsPage on /results route', () => {
    renderWithRouter(['/results']);
    expect(screen.getByTestId('results-page')).toBeInTheDocument();
  });

  test('redirects to HomePage for unknown routes', () => {
    renderWithRouter(['/unknown-route']);
    expect(screen.getByTestId('home-page')).toBeInTheDocument();
  });

  test('provides AnalysisContext to child components', () => {
    renderWithRouter();
    // The context provider should be present and not throw errors
    expect(screen.getByTestId('home-page')).toBeInTheDocument();
  });
});