import React, { createContext, useContext, useReducer, ReactNode } from 'react';

// Types
export interface AnalysisStep {
  step: string;
  step_number: number;
  step_name: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress_percentage: number;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  details?: Record<string, any>;
}

export interface AnalysisProgress {
  analysis_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  overall_progress: number;
  current_step?: AnalysisStep;
  steps: AnalysisStep[];
  started_at: string;
  updated_at: string;
  error?: string;
}

export interface AnalysisResult {
  analysis_id: string;
  session_id: string;
  completed_at: string;
  processing_time: number;
  job_analysis: Record<string, any>;
  company_research: Record<string, any>;
  parsed_resume: Record<string, any>;
  skills_analysis: Record<string, any>;
  resume_recommendations: Record<string, any>;
  cover_letter: Record<string, any>;
  final_summary: Record<string, any>;
  metadata: Record<string, any>;
}

export interface AnalysisHistory {
  analysis_id: string;
  status: string;
  overall_progress: number;
  started_at: string;
  updated_at: string;
  job_description_preview: string;
  job_url?: string;
  preferences: Record<string, any>;
}

export interface AnalysisState {
  currentAnalysis: AnalysisProgress | null;
  analysisHistory: AnalysisHistory[];
  currentResults: AnalysisResult | null;
  loading: boolean;
  error: string | null;
}

export interface AnalysisContextType extends AnalysisState {
  startAnalysis: (jobDescription: string, resumeText: string, preferences?: Record<string, any>) => Promise<string>;
  getProgress: (analysisId: string) => Promise<AnalysisProgress>;
  getResults: (analysisId: string) => Promise<AnalysisResult>;
  cancelAnalysis: (analysisId: string) => Promise<void>;
  loadHistory: () => Promise<void>;
  clearError: () => void;
  clearCurrentAnalysis: () => void;
}

// Actions
type AnalysisAction =
  | { type: 'START_ANALYSIS' }
  | { type: 'ANALYSIS_STARTED'; payload: string }
  | { type: 'UPDATE_PROGRESS'; payload: AnalysisProgress }
  | { type: 'ANALYSIS_COMPLETED'; payload: AnalysisResult }
  | { type: 'ANALYSIS_FAILED'; payload: string }
  | { type: 'LOAD_HISTORY_SUCCESS'; payload: AnalysisHistory[] }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string }
  | { type: 'CLEAR_ERROR' }
  | { type: 'CLEAR_CURRENT_ANALYSIS' };

// Initial state
const initialState: AnalysisState = {
  currentAnalysis: null,
  analysisHistory: [],
  currentResults: null,
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
        currentAnalysis: null,
        currentResults: null,
      };
    case 'ANALYSIS_STARTED':
      return {
        ...state,
        loading: false,
        error: null,
      };
    case 'UPDATE_PROGRESS':
      return {
        ...state,
        currentAnalysis: action.payload,
        error: null,
      };
    case 'ANALYSIS_COMPLETED':
      return {
        ...state,
        currentResults: action.payload,
        loading: false,
        error: null,
      };
    case 'ANALYSIS_FAILED':
      return {
        ...state,
        loading: false,
        error: action.payload,
        currentAnalysis: null,
      };
    case 'LOAD_HISTORY_SUCCESS':
      return {
        ...state,
        analysisHistory: action.payload,
        loading: false,
        error: null,
      };
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        loading: false,
      };
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    case 'CLEAR_CURRENT_ANALYSIS':
      return {
        ...state,
        currentAnalysis: null,
        currentResults: null,
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
  const startAnalysis = async (
    jobDescription: string,
    resumeText: string,
    preferences?: Record<string, any>
  ): Promise<string> => {
    dispatch({ type: 'START_ANALYSIS' });

    try {
      // This will be implemented when we create the API service
      console.log('Starting analysis:', { jobDescription, resumeText, preferences });
      
      // Placeholder response - will be replaced with actual API call
      const analysisId = 'mock_analysis_' + Date.now();
      
      dispatch({ type: 'ANALYSIS_STARTED', payload: analysisId });
      
      return analysisId;
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to start analysis';
      dispatch({ type: 'ANALYSIS_FAILED', payload: errorMessage });
      throw error;
    }
  };

  // Get progress function
  const getProgress = async (analysisId: string): Promise<AnalysisProgress> => {
    try {
      // This will be implemented when we create the API service
      console.log('Getting progress for:', analysisId);
      
      // Placeholder response - will be replaced with actual API call
      const mockProgress: AnalysisProgress = {
        analysis_id: analysisId,
        status: 'processing',
        overall_progress: 50,
        steps: [],
        started_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      
      dispatch({ type: 'UPDATE_PROGRESS', payload: mockProgress });
      
      return mockProgress;
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to get progress';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    }
  };

  // Get results function
  const getResults = async (analysisId: string): Promise<AnalysisResult> => {
    try {
      // This will be implemented when we create the API service
      console.log('Getting results for:', analysisId);
      
      // Placeholder response - will be replaced with actual API call
      throw new Error('API service not yet implemented');
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to get results';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    }
  };

  // Cancel analysis function
  const cancelAnalysis = async (analysisId: string): Promise<void> => {
    try {
      // This will be implemented when we create the API service
      console.log('Cancelling analysis:', analysisId);
      
      // Placeholder - will be replaced with actual API call
      dispatch({ type: 'CLEAR_CURRENT_ANALYSIS' });
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to cancel analysis';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
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
      const mockHistory: AnalysisHistory[] = [];
      
      dispatch({ type: 'LOAD_HISTORY_SUCCESS', payload: mockHistory });
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load history';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
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