import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { 
  AnalysisState, 
  AnalysisAction, 
  ProgressResponse, 
  AnalysisResults,
  SessionInfo,
  JobAnalysisRequest,
  ProcessingStatusEnum
} from '../types';

export interface AnalysisContextType extends AnalysisState {
  startAnalysis: (request: JobAnalysisRequest) => Promise<string>;
  getProgress: (sessionId: string) => Promise<ProgressResponse>;
  getResults: (sessionId: string) => Promise<AnalysisResults>;
  cancelAnalysis: (sessionId: string) => Promise<void>;
  loadHistory: () => Promise<void>;
  clearError: () => void;
  clearCurrentAnalysis: () => void;
}

// Initial state
const initialState: AnalysisState = {
  currentSession: undefined,
  progress: undefined,
  results: undefined,
  history: [],
  loading: false,
  error: null,
};

// Reducer
const analysisReducer = (state: AnalysisState, action: AnalysisAction): AnalysisState => {
  switch (action.type) {
    case 'START_ANALYSIS':
      return {
        ...state,
        loading: true,
        error: null,
        progress: undefined,
        results: undefined,
      };
    case 'ANALYSIS_STARTED':
      return {
        ...state,
        loading: false,
        error: null,
      };
    case 'PROGRESS_UPDATE':
      return {
        ...state,
        progress: action.payload,
        error: null,
      };
    case 'ANALYSIS_COMPLETE':
      return {
        ...state,
        results: action.payload,
        loading: false,
        error: null,
      };
    case 'ANALYSIS_ERROR':
      return {
        ...state,
        loading: false,
        error: action.payload,
        progress: undefined,
      };
    case 'LOAD_HISTORY':
      return {
        ...state,
        history: action.payload,
        loading: false,
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
    case 'CLEAR_CURRENT_ANALYSIS':
      return {
        ...state,
        currentSession: undefined,
        progress: undefined,
        results: undefined,
        error: null,
      };
    default:
      return state;
  }
};

// Context
const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined);

// Provider Props
interface AnalysisProviderProps {
  children: ReactNode;
}

// Provider Component
export const AnalysisProvider: React.FC<AnalysisProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(analysisReducer, initialState);

  // Start analysis function
  const startAnalysis = async (request: JobAnalysisRequest): Promise<string> => {
    dispatch({ type: 'START_ANALYSIS', payload: request });

    try {
      // This will be implemented when we create the API service
      console.log('Starting analysis:', request);
      
      // Placeholder response - will be replaced with actual API call
      const sessionId = 'mock_session_' + Date.now();
      
      dispatch({ type: 'ANALYSIS_STARTED', payload: { session_id: sessionId, status: ProcessingStatusEnum.PENDING, progress: {}, estimated_completion: undefined } });
      
      return sessionId;
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to start analysis';
      dispatch({ type: 'ANALYSIS_ERROR', payload: errorMessage });
      throw error;
    }
  };

  // Get progress function
  const getProgress = async (sessionId: string): Promise<ProgressResponse> => {
    try {
      // This will be implemented when we create the API service
      console.log('Getting progress for:', sessionId);
      
      // Placeholder response - will be replaced with actual API call
      const mockProgress: ProgressResponse = {
        session_id: sessionId,
        status: ProcessingStatusEnum.PROCESSING,
        overall_progress: 50,
        current_step: undefined,
        steps: [],
        estimated_time_remaining: undefined,
        error_message: undefined,
        started_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      
      dispatch({ type: 'PROGRESS_UPDATE', payload: mockProgress });
      
      return mockProgress;
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to get progress';
      dispatch({ type: 'ANALYSIS_ERROR', payload: errorMessage });
      throw error;
    }
  };

  // Get results function
  const getResults = async (sessionId: string): Promise<AnalysisResults> => {
    try {
      // This will be implemented when we create the API service
      console.log('Getting results for:', sessionId);
      
      // Placeholder response - will be replaced with actual API call
      throw new Error('API service not yet implemented');
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to get results';
      dispatch({ type: 'ANALYSIS_ERROR', payload: errorMessage });
      throw error;
    }
  };

  // Cancel analysis function
  const cancelAnalysis = async (sessionId: string): Promise<void> => {
    try {
      // This will be implemented when we create the API service
      console.log('Cancelling analysis:', sessionId);
      
      // Placeholder - will be replaced with actual API call
      dispatch({ type: 'CANCEL_ANALYSIS', payload: sessionId });
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to cancel analysis';
      dispatch({ type: 'ANALYSIS_ERROR', payload: errorMessage });
      throw error;
    }
  };

  // Load history function
  const loadHistory = async (): Promise<void> => {
    dispatch({ type: 'SET_LOADING', payload: true });

    try {
      // This will be implemented when we create the API service
      console.log('Loading analysis history');
      
      // Placeholder response - will be replaced with actual API call
      const mockHistory: SessionInfo[] = [];
      
      dispatch({ type: 'LOAD_HISTORY', payload: mockHistory });
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load history';
      dispatch({ type: 'ANALYSIS_ERROR', payload: errorMessage });
    }
  };

  // Clear error function
  const clearError = (): void => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  // Clear current analysis function
  const clearCurrentAnalysis = (): void => {
    dispatch({ type: 'CLEAR_CURRENT_ANALYSIS' });
  };

  // Context value
  const contextValue: AnalysisContextType = {
    ...state,
    startAnalysis,
    getProgress,
    getResults,
    cancelAnalysis,
    loadHistory,
    clearError,
    clearCurrentAnalysis,
  };

  return (
    <AnalysisContext.Provider value={contextValue}>
      {children}
    </AnalysisContext.Provider>
  );
};

// Hook to use analysis context
export const useAnalysis = (): AnalysisContextType => {
  const context = useContext(AnalysisContext);
  if (context === undefined) {
    throw new Error('useAnalysis must be used within an AnalysisProvider');
  }
  return context;
};