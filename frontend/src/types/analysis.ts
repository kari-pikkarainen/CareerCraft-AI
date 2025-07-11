/**
 * Job analysis workflow TypeScript interfaces
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2024 Kari Pikkarainen. All rights reserved.
 */

import { ProcessingStatusEnum, ToneEnum, PriorityEnum, RequirementCategoryEnum } from './enums';

// Job preferences for analysis
export interface JobPreferences {
  tone: ToneEnum;
  focus_areas: string[]; // max 5 items
  include_salary_guidance: boolean;
  include_interview_prep: boolean;
}

// Job analysis request
export interface JobAnalysisRequest {
  job_description: string; // min 50, max 50000 chars
  job_url?: string;
  preferences: JobPreferences;
}

export interface JobAnalysisResponse {
  session_id: string;
  status: ProcessingStatusEnum;
  progress: Record<string, any>;
  estimated_completion?: string; // ISO date string
}

// Progress tracking
export interface ProgressStep {
  step_number: number; // 1-7
  step_name: string;
  status: ProcessingStatusEnum;
  progress_percentage: number; // 0-100
  started_at?: string; // ISO date string
  completed_at?: string; // ISO date string
  details?: string;
}

export interface ProgressResponse {
  session_id: string;
  status: ProcessingStatusEnum;
  overall_progress: number; // 0-100
  current_step?: ProgressStep;
  steps: ProgressStep[];
  estimated_time_remaining?: string;
  error_message?: string;
  started_at: string; // ISO date string
  updated_at: string; // ISO date string
}

// Skills analysis
export interface SkillAnalysis {
  skill: string;
  required: boolean;
  present_in_resume: boolean;
  proficiency_level?: string;
  importance_score: number; // 0-1
}

// Job requirements
export interface JobRequirement {
  requirement: string;
  category: RequirementCategoryEnum;
  priority: PriorityEnum;
  matches_resume: boolean;
}

// Job analysis results
export interface JobAnalysisResult {
  job_title: string;
  company_name?: string;
  location?: string;
  employment_type?: string;
  experience_level?: string;
  salary_range?: string;
  requirements: JobRequirement[];
  skills_analysis: SkillAnalysis[];
  key_keywords: string[];
  industry?: string;
  remote_friendly?: boolean;
  analysis_score: number; // 0-1
}

// Company research
export interface CompanyInsight {
  category: string;
  title: string;
  content: string;
  source?: string;
  relevance_score: number; // 0-1
}

export interface CompanyResearchResult {
  company_name: string;
  industry?: string;
  size?: string;
  location?: string;
  website?: string;
  mission_statement?: string;
  values: string[];
  culture_keywords: string[];
  recent_news: string[];
  insights: CompanyInsight[];
  research_score: number; // 0-1
}

// Resume analysis
export interface ResumeRecommendation {
  category: string;
  priority: PriorityEnum;
  title: string;
  description: string;
  specific_examples: string[];
  keywords_to_add: string[];
}

export interface ResumeAnalysisResult {
  overall_score: number; // 0-1
  job_match_score: number; // 0-1
  strengths: string[];
  weaknesses: string[];
  missing_keywords: string[];
  recommendations: ResumeRecommendation[];
  sections_analysis: Record<string, Record<string, any>>;
}

// Cover letter
export interface CoverLetterResult {
  content: string;
  tone: ToneEnum;
  word_count: number;
  key_points: string[];
  company_specific_elements: string[];
  customization_score: number; // 0-1
}

// Application strategy
export interface ApplicationStrategyResult {
  overall_fit: number; // 0-1
  application_priority: PriorityEnum;
  strengths_to_highlight: string[];
  potential_concerns: string[];
  addressing_strategies: string[];
  interview_preparation: string[];
  salary_guidance?: Record<string, any>;
  timeline_recommendations: Record<string, string>;
}

// Complete analysis results
export interface AnalysisResults {
  session_id: string;
  job_analysis: JobAnalysisResult;
  company_research: CompanyResearchResult;
  resume_analysis: ResumeAnalysisResult;
  cover_letter: CoverLetterResult;
  application_strategy: ApplicationStrategyResult;
  processing_time: number; // seconds
  completed_at: string; // ISO date string
}

// Session and history
export interface SessionInfo {
  session_id: string;
  created_at: string; // ISO date string
  status: ProcessingStatusEnum;
  job_title?: string;
  company_name?: string;
  progress: number; // 0-100
}

export interface ApplicationHistory {
  sessions: SessionInfo[];
  total_applications: number;
  success_rate: number; // 0-1
  last_activity?: string; // ISO date string
}

// Frontend analysis state management
export interface AnalysisState {
  currentSession?: SessionInfo;
  progress?: ProgressResponse;
  results?: AnalysisResults;
  history: SessionInfo[];
  loading: boolean;
  error: string | null;
}

export type AnalysisAction =
  | { type: 'START_ANALYSIS'; payload: JobAnalysisRequest }
  | { type: 'ANALYSIS_STARTED'; payload: JobAnalysisResponse }
  | { type: 'PROGRESS_UPDATE'; payload: ProgressResponse }
  | { type: 'ANALYSIS_COMPLETE'; payload: AnalysisResults }
  | { type: 'ANALYSIS_ERROR'; payload: string }
  | { type: 'CANCEL_ANALYSIS'; payload: string }
  | { type: 'LOAD_HISTORY'; payload: SessionInfo[] }
  | { type: 'CLEAR_CURRENT_ANALYSIS' }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'CLEAR_ERROR' };