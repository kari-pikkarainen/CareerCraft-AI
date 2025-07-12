/**
 * HomePage Basic Tests
 * Simplified tests to avoid routing complexity
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';

// Mock react-router-dom to avoid complex routing
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
}));

// Import HomePage after mocking
import HomePage from './HomePage';

describe('HomePage Basic Tests', () => {
  test('renders main heading', () => {
    render(<HomePage />);
    expect(screen.getByText('AI-Powered Job Application Analysis')).toBeInTheDocument();
  });

  test('renders brand elements', () => {
    render(<HomePage />);
    expect(screen.getByText('CareerCraft AI')).toBeInTheDocument();
    expect(screen.getByText('Smart Job Analysis')).toBeInTheDocument();
  });

  test('renders features section', () => {
    render(<HomePage />);
    expect(screen.getByText('Powerful AI Analysis Tools')).toBeInTheDocument();
    expect(screen.getByText('Smart Job Analysis')).toBeInTheDocument();
    expect(screen.getByText('Skills Gap Detection')).toBeInTheDocument();
  });

  test('renders how it works section', () => {
    render(<HomePage />);
    expect(screen.getByText('How It Works')).toBeInTheDocument();
    expect(screen.getByText('Upload Your Resume')).toBeInTheDocument();
    expect(screen.getByText('Add Job Details')).toBeInTheDocument();
    expect(screen.getByText('Get AI Analysis')).toBeInTheDocument();
  });

  test('renders footer copyright', () => {
    render(<HomePage />);
    expect(screen.getByText(/© 2025 Kari Pikkarainen/)).toBeInTheDocument();
  });

  test('renders navigation links', () => {
    render(<HomePage />);
    expect(screen.getByText('Features')).toBeInTheDocument();
    expect(screen.getByText('How it Works')).toBeInTheDocument();
  });

  test('renders call-to-action buttons', () => {
    render(<HomePage />);
    expect(screen.getByText('Get Started Free')).toBeInTheDocument();
    expect(screen.getByText('Start Free Analysis')).toBeInTheDocument();
  });

  test('renders ad placeholders', () => {
    render(<HomePage />);
    expect(screen.getByText('Advertisement')).toBeInTheDocument();
    expect(screen.getByText('Sponsored')).toBeInTheDocument();
  });
});