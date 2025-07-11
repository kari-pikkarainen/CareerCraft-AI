import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { User, AuthState, AuthAction, LoginFormData } from '../types';
import { getApiService, processError } from '../services';

export interface AuthContextType extends AuthState {
  login: (credentials: LoginFormData) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  clearError: () => void;
  isAuthenticated: boolean;
}

// Initial state
const initialState: AuthState = {
  user: null,
  token: null,
  loading: true,
  error: null,
  isAuthenticated: false,
};

// Reducer
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'LOGIN_START':
      return {
        ...state,
        loading: true,
        error: null,
      };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        loading: false,
        error: null,
        isAuthenticated: true,
      };
    case 'LOGIN_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        loading: false,
        error: action.payload,
        isAuthenticated: false,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        loading: false,
        error: null,
        isAuthenticated: false,
      };
    case 'TOKEN_REFRESH_SUCCESS':
      return {
        ...state,
        token: action.payload,
        error: null,
      };
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload,
      };
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    default:
      return state;
  }
};

// Context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider Props
interface AuthProviderProps {
  children: ReactNode;
}

// Provider Component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Load authentication state from localStorage on mount
  useEffect(() => {
    const loadAuthState = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        const userStr = localStorage.getItem('auth_user');

        if (token && userStr) {
          const user: User = JSON.parse(userStr);
          
          // Check if token is expired
          const now = new Date();
          const expiresAt = user.expires_at ? new Date(user.expires_at) : null;
          
          if (expiresAt && now < expiresAt) {
            dispatch({ 
              type: 'LOGIN_SUCCESS', 
              payload: { user, token } 
            });
          } else {
            // Token is expired, try to refresh
            try {
              await refreshToken();
            } catch (error) {
              // Refresh failed, clear auth state
              localStorage.removeItem('auth_token');
              localStorage.removeItem('auth_user');
              dispatch({ type: 'LOGOUT' });
            }
          }
        } else {
          dispatch({ type: 'SET_LOADING', payload: false });
        }
      } catch (error) {
        console.error('Error loading auth state:', error);
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    };

    loadAuthState();
  }, []);

  // Login function
  const login = async (credentials: LoginFormData): Promise<void> => {
    dispatch({ type: 'LOGIN_START' });

    try {
      const apiService = getApiService();
      
      // Call authentication API
      const authResponse = await apiService.login({
        client_id: 'frontend-client',
        permissions: ['read', 'write'],
      });
      
      // Create user object from response
      const user: User = {
        id: authResponse.session_id,
        email: credentials.email,
        permissions: authResponse.permissions,
        session_id: authResponse.session_id,
        expires_at: new Date(Date.now() + authResponse.expires_in * 1000),
      };
      
      // Store auth data
      localStorage.setItem('auth_token', authResponse.access_token);
      localStorage.setItem('auth_user', JSON.stringify(user));
      
      // Update state
      dispatch({ 
        type: 'LOGIN_SUCCESS', 
        payload: { user, token: authResponse.access_token } 
      });
      
    } catch (error) {
      const processedError = processError(error, { action: 'login', email: credentials.email });
      dispatch({ type: 'LOGIN_FAILURE', payload: processedError.userMessage });
      throw processedError;
    }
  };

  // Logout function
  const logout = async (): Promise<void> => {
    try {
      // Call logout API endpoint
      const apiService = getApiService();
      await apiService.logout();
      
    } catch (error) {
      console.error('Logout API call failed:', error);
      // Continue with local logout even if API call fails
    } finally {
      // Clear local storage
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
      
      // Update state
      dispatch({ type: 'LOGOUT' });
    }
  };

  // Refresh token function
  const refreshToken = async (): Promise<void> => {
    try {
      if (!state.token) {
        throw new Error('No token to refresh');
      }

      const apiService = getApiService();
      
      // Call token refresh API
      const authResponse = await apiService.refreshToken({
        refresh_token: state.token,
      });
      
      // Update stored token
      localStorage.setItem('auth_token', authResponse.access_token);
      
      // Update state
      dispatch({ 
        type: 'TOKEN_REFRESH_SUCCESS', 
        payload: authResponse.access_token 
      });
      
    } catch (error) {
      console.error('Token refresh failed:', error);
      // Clear auth state on refresh failure
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
      dispatch({ type: 'LOGOUT' });
      throw error;
    }
  };

  // Clear error function
  const clearError = (): void => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  // Context value
  const contextValue: AuthContextType = {
    ...state,
    login,
    logout,
    refreshToken,
    clearError,
    isAuthenticated: !!state.user && !!state.token && !state.loading,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};