/**
 * HomePage Component Tests
 * Basic rendering and navigation tests
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import HomePage from './HomePage';

const mockNavigate = jest.fn();

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('HomePage', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  test('renders main heading', () => {
    renderWithRouter(<HomePage />);
    expect(screen.getByText('AI-Powered Job Application Analysis')).toBeInTheDocument();
  });

  test('renders brand title', () => {
    renderWithRouter(<HomePage />);
    expect(screen.getByText('CareerCraft AI')).toBeInTheDocument();
  });

  test('renders tagline', () => {
    renderWithRouter(<HomePage />);
    expect(screen.getByText('Smart Job Analysis')).toBeInTheDocument();
  });

  test('renders features section', () => {
    renderWithRouter(<HomePage />);
    expect(screen.getByText('Powerful AI Analysis Tools')).toBeInTheDocument();
    expect(screen.getByText('Smart Job Analysis')).toBeInTheDocument();
    expect(screen.getByText('Skills Gap Detection')).toBeInTheDocument();
    expect(screen.getByText('Resume Optimization')).toBeInTheDocument();
  });

  test('renders how it works section', () => {
    renderWithRouter(<HomePage />);
    expect(screen.getByText('How It Works')).toBeInTheDocument();
    expect(screen.getByText('Upload Your Resume')).toBeInTheDocument();
    expect(screen.getByText('Add Job Details')).toBeInTheDocument();
    expect(screen.getByText('Get AI Analysis')).toBeInTheDocument();
  });

  test('navigates to analyze page on Get Started click', () => {
    renderWithRouter(<HomePage />);
    const getStartedButton = screen.getByRole('button', { name: /get started free/i });
    fireEvent.click(getStartedButton);
    expect(mockNavigate).toHaveBeenCalledWith('/analyze');
  });

  test('navigates to analyze page on Start Free Analysis click', () => {
    renderWithRouter(<HomePage />);
    const startAnalysisButton = screen.getByRole('button', { name: /start free analysis/i });
    fireEvent.click(startAnalysisButton);
    expect(mockNavigate).toHaveBeenCalledWith('/analyze');
  });

  test('navigates to analyze page on Start Your Analysis Now click', () => {
    renderWithRouter(<HomePage />);
    const startNowButton = screen.getByRole('button', { name: /start your analysis now/i });
    fireEvent.click(startNowButton);
    expect(mockNavigate).toHaveBeenCalledWith('/analyze');
  });

  test('renders ad placeholders', () => {
    renderWithRouter(<HomePage />);
    expect(screen.getByText('Advertisement')).toBeInTheDocument();
    expect(screen.getByText('Sponsored')).toBeInTheDocument();
  });

  test('renders footer with copyright', () => {
    renderWithRouter(<HomePage />);
    expect(screen.getByText(/© 2025 Kari Pikkarainen/)).toBeInTheDocument();
  });
});