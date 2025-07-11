/**
 * File Upload Component with Drag & Drop
 * Supports resume files (PDF, DOCX, TXT) for job analysis
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2024 Kari Pikkarainen. All rights reserved.
 */

import React, { useState, useRef, useCallback } from 'react';
import './FileUpload.css';

// Supported file types
const SUPPORTED_TYPES = {
  'application/pdf': '.pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
  'application/msword': '.doc',
  'text/plain': '.txt',
};

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const SUPPORTED_EXTENSIONS = Object.values(SUPPORTED_TYPES);

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  onFileRemove: () => void;
  selectedFile?: File | null;
  uploading?: boolean;
  uploadProgress?: number;
  error?: string | null;
  disabled?: boolean;
}

interface FileValidationResult {
  isValid: boolean;
  error?: string;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  onFileRemove,
  selectedFile,
  uploading = false,
  uploadProgress = 0,
  error,
  disabled = false,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Validate file type and size
  const validateFile = useCallback((file: File): FileValidationResult => {
    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return {
        isValid: false,
        error: `File size must be less than ${Math.round(MAX_FILE_SIZE / (1024 * 1024))}MB`,
      };
    }

    // Check file type
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    const isValidType = Object.keys(SUPPORTED_TYPES).includes(file.type) || 
                       SUPPORTED_EXTENSIONS.includes(fileExtension);

    if (!isValidType) {
      return {
        isValid: false,
        error: `File type not supported. Please upload: ${SUPPORTED_EXTENSIONS.join(', ')}`,
      };
    }

    return { isValid: true };
  }, []);

  // Handle file selection
  const handleFileSelect = useCallback((file: File) => {
    const validation = validateFile(file);
    
    if (!validation.isValid) {
      setValidationError(validation.error || 'Invalid file');
      return;
    }

    setValidationError(null);
    onFileSelect(file);
  }, [validateFile, onFileSelect]);

  // Handle file input change
  const handleInputChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  }, [handleFileSelect]);

  // Handle drag events
  const handleDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();
    if (!disabled) {
      setIsDragOver(true);
    }
  }, [disabled]);

  const handleDragLeave = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragOver(false);

    if (disabled) return;

    const files = event.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [disabled, handleFileSelect]);

  // Handle click to open file picker
  const handleClick = useCallback(() => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  }, [disabled]);

  // Handle file removal
  const handleRemove = useCallback((event: React.MouseEvent) => {
    event.stopPropagation();
    setValidationError(null);
    onFileRemove();
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [onFileRemove]);

  // Format file size for display
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Get file icon based on type
  const getFileIcon = (file: File): string => {
    const extension = '.' + file.name.split('.').pop()?.toLowerCase();
    switch (extension) {
      case '.pdf':
        return '📄';
      case '.docx':
      case '.doc':
        return '📝';
      case '.txt':
        return '📃';
      default:
        return '📎';
    }
  };

  const displayError = error || validationError;

  return (
    <div className="file-upload-container">
      {!selectedFile ? (
        // Upload area
        <div
          className={`file-upload-area ${isDragOver ? 'drag-over' : ''} ${disabled ? 'disabled' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleClick}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept={Object.keys(SUPPORTED_TYPES).join(',')}
            onChange={handleInputChange}
            disabled={disabled}
            className="file-input-hidden"
          />
          
          <div className="upload-content">
            <div className="upload-icon">
              {isDragOver ? '📁' : '📤'}
            </div>
            
            <div className="upload-text">
              <h3>
                {isDragOver ? 'Drop your resume here' : 'Upload your resume'}
              </h3>
              <p>
                Drag and drop your file here, or{' '}
                <span className="upload-link">click to browse</span>
              </p>
            </div>
            
            <div className="upload-info">
              <p>Supported formats: PDF, DOCX, DOC, TXT</p>
              <p>Maximum file size: {Math.round(MAX_FILE_SIZE / (1024 * 1024))}MB</p>
            </div>
          </div>
        </div>
      ) : (
        // Selected file display
        <div className="file-selected">
          <div className="file-info">
            <div className="file-icon">
              {getFileIcon(selectedFile)}
            </div>
            
            <div className="file-details">
              <h4 className="file-name">{selectedFile.name}</h4>
              <p className="file-metadata">
                {formatFileSize(selectedFile.size)} • {selectedFile.type || 'Unknown type'}
              </p>
              
              {uploading && (
                <div className="upload-progress">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                  <span className="progress-text">{Math.round(uploadProgress)}%</span>
                </div>
              )}
            </div>
            
            <div className="file-actions">
              {!uploading && (
                <button
                  type="button"
                  className="btn-remove"
                  onClick={handleRemove}
                  disabled={disabled}
                  aria-label="Remove file"
                >
                  ✕
                </button>
              )}
            </div>
          </div>
        </div>
      )}
      
      {displayError && (
        <div className="file-upload-error">
          <span className="error-icon">⚠️</span>
          <span className="error-message">{displayError}</span>
        </div>
      )}
    </div>
  );
};

export default FileUpload;