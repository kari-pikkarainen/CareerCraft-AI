/**
 * CareerCraft AI Services Index
 * Central export point for all services
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

// Service initialization and management imports
import { initializeApiService } from './apiService';
import { configService } from './configService';
import { errorService } from './errorService';

// Core services
export { CareerCraftApiService, initializeApiService, getApiService } from './apiService';
export { ConfigService, configService, isDevelopment, isProduction, getEnvironment } from './configService';
export { ErrorService, errorService, processError, getRecentErrors, ErrorSeverity, ErrorCategory } from './errorService';

/**
 * Initialize all services with configuration
 */
export const initializeServices = () => {
  try {
    // Get API configuration
    const apiConfig = configService.getApiConfig();
    
    // Initialize API service
    const apiService = initializeApiService(apiConfig);
    
    // Log initialization in development
    if (configService.isDevelopment()) {
      console.log('CareerCraft AI Services initialized:', {
        config: configService.getDebugInfo(),
        apiService: !!apiService,
        errorService: !!errorService,
      });
    }
    
    return {
      apiService,
      configService,
      errorService,
    };
  } catch (error) {
    console.error('Failed to initialize services:', error);
    throw error;
  }
};

/**
 * Service health check
 */
export const checkServiceHealth = async () => {
  const results = {
    config: false,
    api: false,
    overall: false,
  };
  
  try {
    // Check config service
    const config = configService.getConfig();
    results.config = !!config;
    
    // Check API service (if credentials are available)
    if (config.api.apiKey && config.api.apiSecret) {
      try {
        const { getApiService } = await import('./apiService');
        const apiService = getApiService();
        await apiService.healthCheck();
        results.api = true;
      } catch (error) {
        console.warn('API health check failed:', error);
        results.api = false;
      }
    }
    
    results.overall = results.config && (results.api || !config.api.apiKey);
    
  } catch (error) {
    console.error('Service health check failed:', error);
  }
  
  return results;
};

// Types re-export for convenience
export type { AppConfig } from './configService';
export type { ProcessedError } from './errorService';