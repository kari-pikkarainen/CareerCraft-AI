/**
 * Simple Component Tests
 * Basic utility component tests
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';

// Simple test component
const TestButton: React.FC<{ onClick: () => void; children: React.ReactNode }> = ({ onClick, children }) => (
  <button onClick={onClick}>{children}</button>
);

const TestCard: React.FC<{ title: string; content: string }> = ({ title, content }) => (
  <div className="card">
    <h3>{title}</h3>
    <p>{content}</p>
  </div>
);

describe('Simple Components', () => {
  test('TestButton renders correctly', () => {
    const mockClick = jest.fn();
    render(<TestButton onClick={mockClick}>Click me</TestButton>);
    
    expect(screen.getByText('Click me')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  test('TestCard renders title and content', () => {
    render(<TestCard title="Test Title" content="Test content here" />);
    
    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByText('Test content here')).toBeInTheDocument();
  });

  test('TestCard has correct structure', () => {
    render(<TestCard title="Sample" content="Sample content" />);
    
    const card = screen.getByText('Sample').closest('.card');
    expect(card).toBeInTheDocument();
    expect(card?.querySelector('h3')).toBeInTheDocument();
    expect(card?.querySelector('p')).toBeInTheDocument();
  });
});