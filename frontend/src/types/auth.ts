/**
 * Authentication-related TypeScript interfaces
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2024 Kari Pikkarainen. All rights reserved.
 */

export interface AuthRequest {
  client_id?: string;
  permissions?: string[];
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  session_id: string;
  permissions: string[];
}

export interface TokenRefreshRequest {
  refresh_token?: string;
}

export interface SessionInfoResponse {
  session_id: string;
  user_id?: string;
  api_key?: string;
  created_at: string; // ISO date string
  expires_at: string; // ISO date string
  permissions: string[];
  time_remaining: string;
}

export interface StatusResponse {
  authenticated: boolean;
  session_id?: string;
  user_id?: string;
  permissions: string[];
  expires_at?: string; // ISO date string
}

// User interface for frontend state management
export interface User {
  id?: string;
  email?: string;
  session_id?: string;
  permissions: string[];
  expires_at?: Date;
}

// Login form data
export interface LoginFormData {
  email: string;
  password: string;
  remember_me?: boolean;
}

// Auth context state
export interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
}

// Auth actions for useReducer
export type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'LOGIN_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'TOKEN_REFRESH_SUCCESS'; payload: string }
  | { type: 'TOKEN_REFRESH_FAILURE' }
  | { type: 'CLEAR_ERROR' }
  | { type: 'SET_LOADING'; payload: boolean };