/**
 * Error Handling Service for CareerCraft AI
 * Centralized error management, logging, and user feedback
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

import { ApiError, ErrorResponse, HttpStatus } from '../types';
import { configService } from './configService';

// Error severity levels
export enum ErrorSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

// Error categories
export enum ErrorCategory {
  AUTHENTICATION = 'authentication',
  AUTHORIZATION = 'authorization',
  VALIDATION = 'validation',
  NETWORK = 'network',
  SERVER = 'server',
  CLIENT = 'client',
  UNKNOWN = 'unknown',
}

// Processed error interface
export interface ProcessedError {
  id: string;
  message: string;
  userMessage: string;
  category: ErrorCategory;
  severity: ErrorSeverity;
  isRetryable: boolean;
  shouldReport: boolean;
  timestamp: Date;
  originalError: any;
  context?: Record<string, any>;
}

/**
 * Error Processing Service
 */
export class ErrorService {
  private static instance: ErrorService | null = null;
  private errorQueue: ProcessedError[] = [];
  private maxQueueSize = 100;

  private constructor() {}

  /**
   * Get singleton instance
   */
  public static getInstance(): ErrorService {
    if (!ErrorService.instance) {
      ErrorService.instance = new ErrorService();
    }
    return ErrorService.instance;
  }

  /**
   * Process and categorize error
   */
  public processError(error: any, context?: Record<string, any>): ProcessedError {
    const processedError: ProcessedError = {
      id: this.generateErrorId(),
      message: this.extractErrorMessage(error),
      userMessage: this.createUserMessage(error),
      category: this.categorizeError(error),
      severity: this.assessSeverity(error),
      isRetryable: this.isRetryable(error),
      shouldReport: this.shouldReport(error),
      timestamp: new Date(),
      originalError: error,
      context,
    };

    // Add to error queue
    this.addToQueue(processedError);

    // Log error
    this.logError(processedError);

    // Report error if needed
    if (processedError.shouldReport) {
      this.reportError(processedError);
    }

    return processedError;
  }

  /**
   * Generate unique error ID
   */
  private generateErrorId(): string {
    return `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Extract error message from various error types
   */
  private extractErrorMessage(error: any): string {
    if (typeof error === 'string') {
      return error;
    }

    if (error instanceof Error) {
      return error.message;
    }

    if (error && typeof error === 'object') {
      // API Error
      if ('message' in error) {
        return error.message;
      }

      // ErrorResponse
      if ('error' in error && 'message' in error) {
        return error.message;
      }

      // HTTP Response
      if ('statusText' in error) {
        return error.statusText;
      }
    }

    return 'Unknown error occurred';
  }

  /**
   * Create user-friendly error message
   */
  private createUserMessage(error: any): string {
    const category = this.categorizeError(error);
    const status = this.getErrorStatus(error);

    switch (category) {
      case ErrorCategory.AUTHENTICATION:
        return 'Please log in to continue. Your session may have expired.';
      
      case ErrorCategory.AUTHORIZATION:
        return 'You do not have permission to perform this action.';
      
      case ErrorCategory.VALIDATION:
        return 'Please check your input and try again.';
      
      case ErrorCategory.NETWORK:
        return 'Connection problem. Please check your internet connection and try again.';
      
      case ErrorCategory.SERVER:
        return 'Our servers are experiencing issues. Please try again in a few minutes.';
      
      default:
        // Provide specific messages for common HTTP status codes
        switch (status) {
          case HttpStatus.NOT_FOUND:
            return 'The requested resource was not found.';
          case HttpStatus.TOO_MANY_REQUESTS:
            return 'Too many requests. Please wait a moment before trying again.';
          case HttpStatus.BAD_REQUEST:
            return 'Invalid request. Please check your input.';
          case HttpStatus.INTERNAL_SERVER_ERROR:
            return 'Server error. Our team has been notified.';
          default:
            return 'Something went wrong. Please try again.';
        }
    }
  }

  /**
   * Categorize error by type and status
   */
  private categorizeError(error: any): ErrorCategory {
    const status = this.getErrorStatus(error);

    if (!status) {
      // Network or client-side errors
      if (error instanceof TypeError && error.message.includes('fetch')) {
        return ErrorCategory.NETWORK;
      }
      return ErrorCategory.CLIENT;
    }

    // Categorize by HTTP status code
    switch (status) {
      case HttpStatus.UNAUTHORIZED:
        return ErrorCategory.AUTHENTICATION;
      case HttpStatus.FORBIDDEN:
        return ErrorCategory.AUTHORIZATION;
      case HttpStatus.BAD_REQUEST:
      case HttpStatus.UNPROCESSABLE_ENTITY:
        return ErrorCategory.VALIDATION;
      case HttpStatus.NOT_FOUND:
      case HttpStatus.CONFLICT:
        return ErrorCategory.CLIENT;
      case HttpStatus.INTERNAL_SERVER_ERROR:
      case HttpStatus.BAD_GATEWAY:
      case HttpStatus.SERVICE_UNAVAILABLE:
      case HttpStatus.GATEWAY_TIMEOUT:
        return ErrorCategory.SERVER;
      default:
        if (status >= 400 && status < 500) {
          return ErrorCategory.CLIENT;
        }
        if (status >= 500) {
          return ErrorCategory.SERVER;
        }
        return ErrorCategory.UNKNOWN;
    }
  }

  /**
   * Assess error severity
   */
  private assessSeverity(error: any): ErrorSeverity {
    const category = this.categorizeError(error);
    const status = this.getErrorStatus(error);

    switch (category) {
      case ErrorCategory.AUTHENTICATION:
      case ErrorCategory.AUTHORIZATION:
        return ErrorSeverity.MEDIUM;
      
      case ErrorCategory.VALIDATION:
        return ErrorSeverity.LOW;
      
      case ErrorCategory.NETWORK:
        return ErrorSeverity.MEDIUM;
      
      case ErrorCategory.SERVER:
        return status === HttpStatus.INTERNAL_SERVER_ERROR ? ErrorSeverity.HIGH : ErrorSeverity.MEDIUM;
      
      default:
        return ErrorSeverity.LOW;
    }
  }

  /**
   * Determine if error is retryable
   */
  private isRetryable(error: any): boolean {
    const category = this.categorizeError(error);
    const status = this.getErrorStatus(error);

    // Non-retryable categories
    if ([ErrorCategory.AUTHENTICATION, ErrorCategory.AUTHORIZATION, ErrorCategory.VALIDATION].includes(category)) {
      return false;
    }

    // Non-retryable status codes
    const nonRetryableStatuses = [
      HttpStatus.BAD_REQUEST,
      HttpStatus.UNAUTHORIZED,
      HttpStatus.FORBIDDEN,
      HttpStatus.NOT_FOUND,
      HttpStatus.UNPROCESSABLE_ENTITY,
    ];

    if (status && nonRetryableStatuses.includes(status)) {
      return false;
    }

    // Retryable network and server errors
    return [ErrorCategory.NETWORK, ErrorCategory.SERVER].includes(category);
  }

  /**
   * Determine if error should be reported
   */
  private shouldReport(error: any): boolean {
    if (!configService.isFeatureEnabled('enableErrorReporting')) {
      return false;
    }

    const severity = this.assessSeverity(error);
    const category = this.categorizeError(error);

    // Always report high and critical severity errors
    if ([ErrorSeverity.HIGH, ErrorSeverity.CRITICAL].includes(severity)) {
      return true;
    }

    // Report server errors in production
    if (configService.isProduction() && category === ErrorCategory.SERVER) {
      return true;
    }

    return false;
  }

  /**
   * Get HTTP status from error
   */
  private getErrorStatus(error: any): number | null {
    if (error && typeof error === 'object') {
      if ('status' in error && typeof error.status === 'number') {
        return error.status;
      }
      if ('response' in error && error.response && 'status' in error.response) {
        return error.response.status;
      }
    }
    return null;
  }

  /**
   * Add error to queue
   */
  private addToQueue(error: ProcessedError): void {
    this.errorQueue.push(error);
    
    // Maintain queue size
    if (this.errorQueue.length > this.maxQueueSize) {
      this.errorQueue.shift();
    }
  }

  /**
   * Log error to console
   */
  private logError(error: ProcessedError): void {
    const logLevel = this.getLogLevel(error.severity);
    const logMessage = `[${error.category.toUpperCase()}] ${error.message}`;
    
    console[logLevel](logMessage, {
      id: error.id,
      severity: error.severity,
      timestamp: error.timestamp,
      context: error.context,
      originalError: error.originalError,
    });
  }

  /**
   * Get console log level for severity
   */
  private getLogLevel(severity: ErrorSeverity): 'log' | 'warn' | 'error' {
    switch (severity) {
      case ErrorSeverity.LOW:
        return 'log';
      case ErrorSeverity.MEDIUM:
        return 'warn';
      case ErrorSeverity.HIGH:
      case ErrorSeverity.CRITICAL:
        return 'error';
      default:
        return 'log';
    }
  }

  /**
   * Report error to external service
   */
  private reportError(error: ProcessedError): void {
    // In a real application, this would send to error reporting service
    // like Sentry, Rollbar, or custom logging endpoint
    if (configService.isDevelopment()) {
      console.warn('Error reporting not implemented for development environment');
      return;
    }

    // TODO: Implement error reporting to external service
    console.info('Error reported:', error.id);
  }

  /**
   * Get recent errors
   */
  public getRecentErrors(limit: number = 20): ProcessedError[] {
    return this.errorQueue.slice(-limit);
  }

  /**
   * Clear error queue
   */
  public clearErrors(): void {
    this.errorQueue = [];
  }

  /**
   * Get error statistics
   */
  public getErrorStats() {
    const now = new Date();
    const lastHour = new Date(now.getTime() - 60 * 60 * 1000);
    
    const recentErrors = this.errorQueue.filter(error => error.timestamp >= lastHour);
    
    const categoryCounts = recentErrors.reduce((acc, error) => {
      acc[error.category] = (acc[error.category] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const severityCounts = recentErrors.reduce((acc, error) => {
      acc[error.severity] = (acc[error.severity] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      total: this.errorQueue.length,
      lastHour: recentErrors.length,
      categories: categoryCounts,
      severities: severityCounts,
    };
  }
}

// Export singleton instance
export const errorService = ErrorService.getInstance();

// Utility functions
export const processError = (error: any, context?: Record<string, any>) => 
  errorService.processError(error, context);

export const getRecentErrors = (limit?: number) => 
  errorService.getRecentErrors(limit);

export default errorService;