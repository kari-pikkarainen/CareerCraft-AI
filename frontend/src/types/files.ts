/**
 * File upload and processing TypeScript interfaces
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2024 Kari Pikkarainen. All rights reserved.
 */

import { FileFormatEnum, ProcessingStatusEnum } from './enums';

export interface FileInfo {
  filename: string;
  file_format: FileFormatEnum;
  file_size: number; // bytes, minimum 1
  content_type: string;
  upload_timestamp: string; // ISO date string
}

export interface FileUploadResponse {
  file_id: string;
  file_info: FileInfo;
  processing_status: ProcessingStatusEnum;
  message: string;
}

// Frontend-specific file upload interfaces
export interface FileUploadProgress {
  file_id?: string;
  progress: number; // 0-100
  status: 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
}

export interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  uploaded_at: Date;
  status: ProcessingStatusEnum;
  url?: string; // For downloading
}

// File validation constraints
export interface FileValidationRules {
  maxSize: number; // in bytes
  allowedTypes: string[]; // MIME types
  allowedExtensions: string[];
}

// File upload form data
export interface FileUploadFormData {
  file: File;
  description?: string;
}

// Drag and drop file interface
export interface DroppedFile {
  file: File;
  id: string; // temporary ID for UI
  preview?: string; // for images
  error?: string;
  status: 'pending' | 'uploading' | 'completed' | 'error';
  progress: number;
}

// File management state
export interface FileState {
  files: UploadedFile[];
  uploading: DroppedFile[];
  loading: boolean;
  error: string | null;
}

export type FileAction =
  | { type: 'UPLOAD_START'; payload: DroppedFile }
  | { type: 'UPLOAD_PROGRESS'; payload: { id: string; progress: number } }
  | { type: 'UPLOAD_SUCCESS'; payload: { tempId: string; file: UploadedFile } }
  | { type: 'UPLOAD_ERROR'; payload: { id: string; error: string } }
  | { type: 'DELETE_FILE'; payload: string }
  | { type: 'CLEAR_UPLOADS' }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null };