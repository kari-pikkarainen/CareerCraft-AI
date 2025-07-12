/**
 * AnalysisContext Tests
 * Context provider and hook tests
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { AnalysisProvider, useAnalysis } from './AnalysisContext';

// Test component that uses the context
const TestComponent: React.FC = () => {
  const context = useAnalysis();
  
  return (
    <div>
      <div data-testid="context-exists">{context ? 'Context exists' : 'No context'}</div>
      <div data-testid="has-methods">
        {typeof context.startAnalysis === 'function' ? 'Has startAnalysis' : 'Missing startAnalysis'}
      </div>
      <div data-testid="has-progress">
        {typeof context.getProgress === 'function' ? 'Has getProgress' : 'Missing getProgress'}
      </div>
      <div data-testid="has-results">
        {typeof context.getResults === 'function' ? 'Has getResults' : 'Missing getResults'}
      </div>
    </div>
  );
};

describe('AnalysisContext', () => {
  test('provides context to children', () => {
    render(
      <AnalysisProvider>
        <TestComponent />
      </AnalysisProvider>
    );
    
    expect(screen.getByTestId('context-exists')).toHaveTextContent('Context exists');
  });

  test('provides required methods', () => {
    render(
      <AnalysisProvider>
        <TestComponent />
      </AnalysisProvider>
    );
    
    expect(screen.getByTestId('has-methods')).toHaveTextContent('Has startAnalysis');
    expect(screen.getByTestId('has-progress')).toHaveTextContent('Has getProgress');
    expect(screen.getByTestId('has-results')).toHaveTextContent('Has getResults');
  });

  test('throws error when used outside provider', () => {
    // Capture console.error to avoid test noise
    const originalError = console.error;
    console.error = jest.fn();
    
    expect(() => {
      render(<TestComponent />);
    }).toThrow('useAnalysis must be used within an AnalysisProvider');
    
    console.error = originalError;
  });
});