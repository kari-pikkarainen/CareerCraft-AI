/**
 * API response and error handling TypeScript interfaces
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

import { EnvironmentEnum } from './enums';

// Base response interface
export interface BaseResponse {
  timestamp: string; // ISO date string
  success: boolean;
}

// Error responses
export interface ErrorResponse {
  error: boolean;
  error_code: string;
  message: string;
  details?: string;
  timestamp: string; // ISO date string
}

export interface ValidationError {
  field: string;
  message: string;
  invalid_value?: any;
}

// Health check responses
export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  environment?: EnvironmentEnum;
  timestamp: string; // ISO date string
  checks: Record<string, string>;
}

export interface DetailedHealthResponse extends HealthResponse {
  uptime?: string;
  configuration?: Record<string, any>;
  security?: Record<string, any>;
  dependencies?: Record<string, any>;
  performance?: Record<string, any>;
}

// API request configuration
export interface ApiRequestConfig {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  url: string;
  data?: any;
  params?: Record<string, string>;
  headers?: Record<string, string>;
  timeout?: number;
  withCredentials?: boolean;
}

// API response wrapper
export interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
  headers: Record<string, string>;
  config: ApiRequestConfig;
}

// API error interface
export interface ApiError {
  message: string;
  status?: number;
  code?: string;
  details?: any;
  timestamp: Date;
}

// Pagination interface for list endpoints
export interface PaginationParams {
  page?: number;
  limit?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// HMAC authentication headers
export interface HMACHeaders {
  'X-API-Key': string;
  'X-Signature': string;
  'X-Timestamp': string;
  'Content-Type': string;
  'Authorization'?: string; // Bearer token for authenticated requests
  [key: string]: string | undefined;
}

// API client configuration
export interface ApiClientConfig {
  baseURL: string;
  apiKey: string;
  timeout: number;
  retries: number;
  retryDelay: number;
}

// Request retry configuration
export interface RetryConfig {
  maxRetries: number;
  retryDelay: number;
  retryCondition?: (error: ApiError) => boolean;
}

// WebSocket message types for real-time progress
export interface WebSocketMessage {
  type: 'progress' | 'error' | 'complete' | 'ping' | 'pong';
  session_id?: string;
  data?: any;
  timestamp: string;
}

// Form validation error structure
export interface FormErrors {
  [field: string]: string[];
}

// API endpoints enum for type safety
export enum ApiEndpoints {
  // Authentication
  AUTH_LOGIN = '/auth/login',
  AUTH_REFRESH = '/auth/refresh',
  AUTH_LOGOUT = '/auth/logout',
  AUTH_STATUS = '/auth/status',
  
  // Files
  FILES_UPLOAD = '/api/v1/files/upload',
  FILES_DOWNLOAD = '/api/v1/files/{file_id}',
  FILES_DELETE = '/api/v1/files/{file_id}',
  
  // Analysis
  ANALYSIS_START = '/api/v1/analyze-application',
  ANALYSIS_PROGRESS = '/api/v1/analysis/{analysis_id}/progress',
  ANALYSIS_RESULTS = '/api/v1/analysis/{analysis_id}/results',
  ANALYSIS_CANCEL = '/api/v1/analysis/{analysis_id}/cancel',
  ANALYSIS_HISTORY = '/api/v1/analysis/history',
  ANALYSIS_CLEANUP = '/api/v1/analysis/cleanup',
  ANALYSIS_HEALTH = '/api/v1/analysis/health',
  
  // Health
  HEALTH = '/health',
  HEALTH_DETAILED = '/health/detailed',
}

// HTTP status codes enum
export enum HttpStatus {
  OK = 200,
  CREATED = 201,
  NO_CONTENT = 204,
  BAD_REQUEST = 400,
  UNAUTHORIZED = 401,
  FORBIDDEN = 403,
  NOT_FOUND = 404,
  CONFLICT = 409,
  UNPROCESSABLE_ENTITY = 422,
  TOO_MANY_REQUESTS = 429,
  INTERNAL_SERVER_ERROR = 500,
  BAD_GATEWAY = 502,
  SERVICE_UNAVAILABLE = 503,
  GATEWAY_TIMEOUT = 504,
}