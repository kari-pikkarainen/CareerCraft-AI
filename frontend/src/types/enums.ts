/**
 * TypeScript enums matching backend Pydantic enums
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2024 Kari Pikkarainen. All rights reserved.
 */

export enum EnvironmentEnum {
  DEVELOPMENT = 'development',
  STAGING = 'staging',
  PRODUCTION = 'production'
}

export enum ProcessingStatusEnum {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export enum FileFormatEnum {
  PDF = 'pdf',
  DOCX = 'docx',
  TXT = 'txt'
}

export enum ToneEnum {
  PROFESSIONAL = 'professional',
  CONVERSATIONAL = 'conversational',
  CONFIDENT = 'confident',
  ENTHUSIASTIC = 'enthusiastic'
}

// Priority levels for recommendations and requirements
export enum PriorityEnum {
  HIGH = 'high',
  MEDIUM = 'medium', 
  LOW = 'low'
}

// Requirement categories
export enum RequirementCategoryEnum {
  TECHNICAL = 'technical',
  SOFT_SKILLS = 'soft_skills',
  EDUCATION = 'education',
  EXPERIENCE = 'experience',
  CERTIFICATIONS = 'certifications',
  OTHER = 'other'
}