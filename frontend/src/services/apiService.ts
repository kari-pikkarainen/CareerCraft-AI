/**
 * CareerCraft AI API Service with HMAC Authentication
 * Provides secure communication with the FastAPI backend
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

import CryptoJS from 'crypto-js';
import {
  ApiEndpoints,
  HttpStatus,
  AuthRequest,
  AuthResponse,
  TokenRefreshRequest,
  StatusResponse,
  JobAnalysisRequest,
  JobAnalysisResponse,
  ProgressResponse,
  AnalysisResults,
  FileUploadResponse,
  ErrorResponse,
  HealthResponse,
  SessionInfo,
  ApplicationHistory,
  ApiResponse,
  ApiError,
  HMACHeaders,
} from '../types';

// API Configuration
interface ApiConfig {
  baseURL: string;
  apiKey: string;
  apiSecret: string;
  timeout: number;
  maxRetries: number;
  retryDelay: number;
}

// Request options interface
interface RequestOptions {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  endpoint: string;
  body?: any;
  headers?: Record<string, string>;
  isFormData?: boolean;
  skipAuth?: boolean;
  timeout?: number;
}

/**
 * CareerCraft AI API Service
 * Handles all communication with the backend using HMAC authentication
 */
export class CareerCraftApiService {
  private config: ApiConfig;
  private jwtToken: string | null = null;

  constructor(config: Partial<ApiConfig>) {
    this.config = {
      baseURL: config.baseURL || 'http://localhost:8000',
      apiKey: config.apiKey || '',
      apiSecret: config.apiSecret || '',
      timeout: config.timeout || 30000, // 30 seconds
      maxRetries: config.maxRetries || 3,
      retryDelay: config.retryDelay || 1000, // 1 second
    };

    if (!this.config.apiKey || !this.config.apiSecret) {
      throw new Error('API key and secret are required');
    }
  }

  /**
   * Generate ISO timestamp in the format expected by backend
   */
  private generateTimestamp(): string {
    return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
  }

  /**
   * Generate HMAC-SHA256 signature for request authentication
   */
  private generateSignature(apiKey: string, timestamp: string, body: string): string {
    // Create message in exact format expected by backend: api_key + "\n" + timestamp + "\n" + body
    const message = `${apiKey}\n${timestamp}\n${body}`;
    
    // Generate HMAC-SHA256 signature
    const signature = CryptoJS.HmacSHA256(message, this.config.apiSecret);
    
    // Convert to Base64 string
    return CryptoJS.enc.Base64.stringify(signature);
  }

  /**
   * Create authentication headers for HMAC-signed requests
   */
  private createAuthHeaders(body: string = '', contentType?: string): Record<string, string> {
    const timestamp = this.generateTimestamp();
    const signature = this.generateSignature(this.config.apiKey, timestamp, body);

    const headers: Record<string, string> = {
      'X-API-Key': this.config.apiKey,
      'X-Signature': signature,
      'X-Timestamp': timestamp,
      'Content-Type': contentType || 'application/json',
    };

    // Add JWT token if available
    if (this.jwtToken) {
      headers.Authorization = `Bearer ${this.jwtToken}`;
    }

    return headers;
  }

  /**
   * Handle API errors and create structured error objects
   */
  private async handleApiError(response: Response): Promise<never> {
    let errorData: ErrorResponse;
    
    try {
      errorData = await response.json();
    } catch {
      errorData = {
        error: true,
        error_code: `HTTP_${response.status}`,
        message: response.statusText || 'Unknown error',
        timestamp: new Date().toISOString(),
      };
    }

    const apiError: ApiError = {
      message: errorData.message || `HTTP ${response.status}`,
      status: response.status,
      code: errorData.error_code,
      details: errorData.details,
      timestamp: new Date(),
    };

    throw apiError;
  }

  /**
   * Retry logic for failed requests
   */
  private async sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Make HTTP request with HMAC authentication and retry logic
   */
  private async makeRequest<T>(options: RequestOptions): Promise<ApiResponse<T>> {
    const url = `${this.config.baseURL}${options.endpoint}`;
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= this.config.maxRetries; attempt++) {
      try {
        // Prepare request body
        let body: string | FormData | undefined;
        let headers: Record<string, string>;

        if (options.isFormData && options.body instanceof FormData) {
          // For FormData, don't stringify and don't set Content-Type (browser sets it with boundary)
          body = options.body;
          headers = this.createAuthHeaders(''); // Empty body for FormData signature
          delete (headers as any)['Content-Type']; // Let browser set multipart boundary
        } else if (options.body) {
          body = JSON.stringify(options.body);
          headers = this.createAuthHeaders(body as string);
        } else {
          body = undefined;
          headers = this.createAuthHeaders('');
        }

        // Add custom headers
        if (options.headers) {
          headers = { ...headers, ...options.headers };
        }

        // Create AbortController for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), options.timeout || this.config.timeout);

        // Make request
        const response = await fetch(url, {
          method: options.method,
          headers,
          body,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        // Handle error responses
        if (!response.ok) {
          await this.handleApiError(response);
        }

        // Parse response
        const data = await response.json();

        // Create response object
        const apiResponse: ApiResponse<T> = {
          data,
          status: response.status,
          statusText: response.statusText,
          headers: Object.fromEntries(response.headers.entries()),
          config: {
            method: options.method,
            url,
            data: options.body,
            headers,
          },
        };

        return apiResponse;

      } catch (error) {
        lastError = error as Error;

        // Don't retry on authentication errors or client errors
        if (error instanceof Error && 'status' in error) {
          const status = (error as any).status;
          if (status >= 400 && status < 500) {
            throw error;
          }
        }

        // Don't retry on the last attempt
        if (attempt === this.config.maxRetries) {
          break;
        }

        // Wait before retrying
        await this.sleep(this.config.retryDelay * attempt);
      }
    }

    // If we get here, all retries failed
    throw lastError || new Error('All retry attempts failed');
  }

  /**
   * Set JWT token for authenticated requests
   */
  public setJwtToken(token: string | null): void {
    this.jwtToken = token;
  }

  /**
   * Get current JWT token
   */
  public getJwtToken(): string | null {
    return this.jwtToken;
  }

  // =============================================================================
  // AUTHENTICATION ENDPOINTS
  // =============================================================================

  /**
   * Login to get JWT token
   */
  public async login(request: AuthRequest = {}): Promise<AuthResponse> {
    const response = await this.makeRequest<AuthResponse>({
      method: 'POST',
      endpoint: ApiEndpoints.AUTH_LOGIN,
      body: request,
    });

    // Store JWT token for future requests
    this.setJwtToken(response.data.access_token);

    return response.data;
  }

  /**
   * Refresh JWT token
   */
  public async refreshToken(request: TokenRefreshRequest = {}): Promise<AuthResponse> {
    const response = await this.makeRequest<AuthResponse>({
      method: 'POST',
      endpoint: ApiEndpoints.AUTH_REFRESH,
      body: request,
    });

    // Update stored JWT token
    this.setJwtToken(response.data.access_token);

    return response.data;
  }

  /**
   * Get authentication status
   */
  public async getAuthStatus(): Promise<StatusResponse> {
    const response = await this.makeRequest<StatusResponse>({
      method: 'GET',
      endpoint: ApiEndpoints.AUTH_STATUS,
    });

    return response.data;
  }

  /**
   * Logout and invalidate session
   */
  public async logout(): Promise<void> {
    try {
      await this.makeRequest<void>({
        method: 'POST',
        endpoint: ApiEndpoints.AUTH_LOGOUT,
      });
    } finally {
      // Clear JWT token regardless of API call success
      this.setJwtToken(null);
    }
  }

  // =============================================================================
  // FILE MANAGEMENT ENDPOINTS
  // =============================================================================

  /**
   * Upload resume file
   */
  public async uploadFile(file: File, extractImmediately: boolean = true): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('extract_immediately', String(extractImmediately));

    const response = await this.makeRequest<FileUploadResponse>({
      method: 'POST',
      endpoint: ApiEndpoints.FILES_UPLOAD,
      body: formData,
      isFormData: true,
    });

    return response.data;
  }

  /**
   * Download file by ID
   */
  public async downloadFile(fileId: string): Promise<Blob> {
    const endpoint = ApiEndpoints.FILES_DOWNLOAD.replace('{file_id}', fileId);
    
    const response = await fetch(`${this.config.baseURL}${endpoint}`, {
      headers: this.createAuthHeaders(''),
    });

    if (!response.ok) {
      await this.handleApiError(response);
    }

    return response.blob();
  }

  /**
   * Delete file by ID
   */
  public async deleteFile(fileId: string): Promise<void> {
    const endpoint = ApiEndpoints.FILES_DELETE.replace('{file_id}', fileId);
    
    await this.makeRequest<void>({
      method: 'DELETE',
      endpoint,
    });
  }

  // =============================================================================
  // JOB ANALYSIS ENDPOINTS
  // =============================================================================

  /**
   * Start job analysis workflow
   */
  public async startJobAnalysis(request: JobAnalysisRequest, resumeFile?: File): Promise<JobAnalysisResponse> {
    const formData = new FormData();
    
    // Add job analysis request fields
    formData.append('job_description', request.job_description);
    if (request.job_url) {
      formData.append('job_url', request.job_url);
    }
    
    // Add preferences
    formData.append('tone', request.preferences.tone);
    formData.append('focus_areas', request.preferences.focus_areas.join(','));
    formData.append('include_salary_guidance', String(request.preferences.include_salary_guidance));
    formData.append('include_interview_prep', String(request.preferences.include_interview_prep));
    
    // Add resume file if provided
    if (resumeFile) {
      formData.append('resume_file', resumeFile);
    }

    const response = await this.makeRequest<JobAnalysisResponse>({
      method: 'POST',
      endpoint: ApiEndpoints.ANALYSIS_START,
      body: formData,
      isFormData: true,
    });

    return response.data;
  }

  /**
   * Get analysis progress
   */
  public async getAnalysisProgress(analysisId: string): Promise<ProgressResponse> {
    const endpoint = ApiEndpoints.ANALYSIS_PROGRESS.replace('{analysis_id}', analysisId);
    
    const response = await this.makeRequest<ProgressResponse>({
      method: 'GET',
      endpoint,
    });

    return response.data;
  }

  /**
   * Get analysis results
   */
  public async getAnalysisResults(analysisId: string): Promise<AnalysisResults> {
    const endpoint = ApiEndpoints.ANALYSIS_RESULTS.replace('{analysis_id}', analysisId);
    
    const response = await this.makeRequest<AnalysisResults>({
      method: 'GET',
      endpoint,
    });

    return response.data;
  }

  /**
   * Cancel running analysis
   */
  public async cancelAnalysis(analysisId: string): Promise<void> {
    const endpoint = ApiEndpoints.ANALYSIS_CANCEL.replace('{analysis_id}', analysisId);
    
    await this.makeRequest<void>({
      method: 'POST',
      endpoint,
    });
  }

  /**
   * Get analysis history
   */
  public async getAnalysisHistory(page: number = 1, limit: number = 20): Promise<ApplicationHistory> {
    const response = await this.makeRequest<ApplicationHistory>({
      method: 'GET',
      endpoint: `${ApiEndpoints.ANALYSIS_HISTORY}?page=${page}&limit=${limit}`,
    });

    return response.data;
  }

  /**
   * Clean up old analysis sessions (admin)
   */
  public async cleanupAnalysis(): Promise<void> {
    await this.makeRequest<void>({
      method: 'POST',
      endpoint: ApiEndpoints.ANALYSIS_CLEANUP,
    });
  }

  // =============================================================================
  // HEALTH CHECK ENDPOINTS
  // =============================================================================

  /**
   * Basic health check
   */
  public async healthCheck(): Promise<HealthResponse> {
    const response = await this.makeRequest<HealthResponse>({
      method: 'GET',
      endpoint: ApiEndpoints.HEALTH,
      skipAuth: true, // Health check doesn't require authentication
    });

    return response.data;
  }

  /**
   * Detailed health check
   */
  public async detailedHealthCheck(): Promise<HealthResponse> {
    const response = await this.makeRequest<HealthResponse>({
      method: 'GET',
      endpoint: ApiEndpoints.HEALTH_DETAILED,
    });

    return response.data;
  }
}

// Default API service instance
let defaultApiService: CareerCraftApiService | null = null;

/**
 * Initialize default API service instance
 */
export const initializeApiService = (config: Partial<ApiConfig>): CareerCraftApiService => {
  defaultApiService = new CareerCraftApiService(config);
  return defaultApiService;
};

/**
 * Get default API service instance
 */
export const getApiService = (): CareerCraftApiService => {
  if (!defaultApiService) {
    throw new Error('API service not initialized. Call initializeApiService() first.');
  }
  return defaultApiService;
};

export default CareerCraftApiService;