/**
 * Configuration Service for CareerCraft AI
 * Manages API credentials, environment settings, and configuration
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

import { EnvironmentEnum } from '../types';

// Configuration interface
export interface AppConfig {
  // API Configuration
  api: {
    baseURL: string;
    apiKey: string;
    apiSecret: string;
    timeout: number;
    maxRetries: number;
    retryDelay: number;
  };
  
  // Environment
  environment: EnvironmentEnum;
  
  // Feature flags
  features: {
    enableAnalytics: boolean;
    enableErrorReporting: boolean;
    enableDarkMode: boolean;
    enableRealTimeUpdates: boolean;
  };
  
  // UI Configuration
  ui: {
    defaultTheme: 'light' | 'dark' | 'system';
    itemsPerPage: number;
    maxFileSize: number; // in bytes
    allowedFileTypes: string[];
  };
}

// Default configuration
const defaultConfig: AppConfig = {
  api: {
    baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
    apiKey: process.env.REACT_APP_API_KEY || '',
    apiSecret: process.env.REACT_APP_API_SECRET || '',
    timeout: 30000, // 30 seconds
    maxRetries: 3,
    retryDelay: 1000, // 1 second
  },
  
  environment: (process.env.REACT_APP_ENVIRONMENT as EnvironmentEnum) || EnvironmentEnum.DEVELOPMENT,
  
  features: {
    enableAnalytics: process.env.REACT_APP_ENABLE_ANALYTICS === 'true',
    enableErrorReporting: process.env.REACT_APP_ENABLE_ERROR_REPORTING === 'true',
    enableDarkMode: process.env.REACT_APP_ENABLE_DARK_MODE !== 'false', // enabled by default
    enableRealTimeUpdates: process.env.REACT_APP_ENABLE_REAL_TIME_UPDATES !== 'false', // enabled by default
  },
  
  ui: {
    defaultTheme: (process.env.REACT_APP_DEFAULT_THEME as 'light' | 'dark' | 'system') || 'system',
    itemsPerPage: parseInt(process.env.REACT_APP_ITEMS_PER_PAGE || '20', 10),
    maxFileSize: parseInt(process.env.REACT_APP_MAX_FILE_SIZE || '10485760', 10), // 10MB
    allowedFileTypes: (process.env.REACT_APP_ALLOWED_FILE_TYPES || 'pdf,docx,txt').split(','),
  },
};

/**
 * Configuration Service Class
 */
export class ConfigService {
  private static instance: ConfigService | null = null;
  private config: AppConfig;

  private constructor() {
    this.config = { ...defaultConfig };
    this.validateConfig();
  }

  /**
   * Get singleton instance
   */
  public static getInstance(): ConfigService {
    if (!ConfigService.instance) {
      ConfigService.instance = new ConfigService();
    }
    return ConfigService.instance;
  }

  /**
   * Validate configuration
   */
  private validateConfig(): void {
    const errors: string[] = [];

    // Validate API configuration
    if (!this.config.api.baseURL) {
      errors.push('API base URL is required');
    }

    if (!this.config.api.apiKey) {
      console.warn('API key not configured. Set REACT_APP_API_KEY environment variable.');
    }

    if (!this.config.api.apiSecret) {
      console.warn('API secret not configured. Set REACT_APP_API_SECRET environment variable.');
    }

    // Validate timeouts
    if (this.config.api.timeout <= 0) {
      errors.push('API timeout must be positive');
    }

    if (this.config.api.maxRetries < 0) {
      errors.push('Max retries cannot be negative');
    }

    // Validate file size
    if (this.config.ui.maxFileSize <= 0) {
      errors.push('Max file size must be positive');
    }

    if (errors.length > 0) {
      throw new Error(`Configuration errors: ${errors.join(', ')}`);
    }
  }

  /**
   * Get complete configuration
   */
  public getConfig(): Readonly<AppConfig> {
    return this.config;
  }

  /**
   * Get API configuration
   */
  public getApiConfig() {
    return this.config.api;
  }

  /**
   * Get environment
   */
  public getEnvironment(): EnvironmentEnum {
    return this.config.environment;
  }

  /**
   * Check if running in development
   */
  public isDevelopment(): boolean {
    return this.config.environment === EnvironmentEnum.DEVELOPMENT;
  }

  /**
   * Check if running in production
   */
  public isProduction(): boolean {
    return this.config.environment === EnvironmentEnum.PRODUCTION;
  }

  /**
   * Check if feature is enabled
   */
  public isFeatureEnabled(feature: keyof AppConfig['features']): boolean {
    return this.config.features[feature];
  }

  /**
   * Get UI configuration
   */
  public getUiConfig() {
    return this.config.ui;
  }

  /**
   * Get max file size in bytes
   */
  public getMaxFileSize(): number {
    return this.config.ui.maxFileSize;
  }

  /**
   * Get max file size in human readable format
   */
  public getMaxFileSizeFormatted(): string {
    const bytes = this.config.ui.maxFileSize;
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Get allowed file types
   */
  public getAllowedFileTypes(): string[] {
    return [...this.config.ui.allowedFileTypes];
  }

  /**
   * Check if file type is allowed
   */
  public isFileTypeAllowed(filename: string): boolean {
    const extension = filename.toLowerCase().split('.').pop();
    return extension ? this.config.ui.allowedFileTypes.includes(extension) : false;
  }

  /**
   * Update configuration (for testing or runtime changes)
   */
  public updateConfig(updates: Partial<AppConfig>): void {
    this.config = { ...this.config, ...updates };
    this.validateConfig();
  }

  /**
   * Get API headers for debugging
   */
  public getDebugInfo() {
    return {
      environment: this.config.environment,
      apiBaseURL: this.config.api.baseURL,
      hasApiKey: !!this.config.api.apiKey,
      hasApiSecret: !!this.config.api.apiSecret,
      features: this.config.features,
      maxFileSize: this.getMaxFileSizeFormatted(),
      allowedFileTypes: this.config.ui.allowedFileTypes,
    };
  }
}

// Export singleton instance
export const configService = ConfigService.getInstance();

// Environment check helpers
export const isDevelopment = () => configService.isDevelopment();
export const isProduction = () => configService.isProduction();
export const getEnvironment = () => configService.getEnvironment();

// Quick access to common config values
export const API_BASE_URL = configService.getApiConfig().baseURL;
export const MAX_FILE_SIZE = configService.getMaxFileSize();
export const ALLOWED_FILE_TYPES = configService.getAllowedFileTypes();

export default configService;