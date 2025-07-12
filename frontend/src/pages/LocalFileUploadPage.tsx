/**
 * Local File Upload Page - Test file upload functionality
 * Direct access to file upload workflow for testing
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

import React, { useState, useCallback } from 'react';
import FileUpload from '../components/FileUpload';
import './LocalFileUploadPage.css';

interface UploadState {
  file: File | null;
  uploading: boolean;
  uploadProgress: number;
  error: string | null;
  success: boolean;
}

const LocalFileUploadPage: React.FC = () => {
  const [uploadState, setUploadState] = useState<UploadState>({
    file: null,
    uploading: false,
    uploadProgress: 0,
    error: null,
    success: false,
  });

  // Handle file selection
  const handleFileSelect = useCallback((file: File) => {
    setUploadState(prev => ({
      ...prev,
      file,
      error: null,
      success: false,
    }));
  }, []);

  // Handle file removal
  const handleFileRemove = useCallback(() => {
    setUploadState(prev => ({
      ...prev,
      file: null,
      error: null,
      success: false,
      uploading: false,
      uploadProgress: 0,
    }));
  }, []);

  // Simulate file upload
  const handleUpload = useCallback(async () => {
    if (!uploadState.file) return;

    setUploadState(prev => ({
      ...prev,
      uploading: true,
      uploadProgress: 0,
      error: null,
      success: false,
    }));

    try {
      // Simulate upload progress
      for (let progress = 0; progress <= 100; progress += 10) {
        await new Promise(resolve => setTimeout(resolve, 200));
        setUploadState(prev => ({
          ...prev,
          uploadProgress: progress,
        }));
      }

      // Simulate success
      setUploadState(prev => ({
        ...prev,
        uploading: false,
        success: true,
      }));

      console.log('File uploaded successfully:', uploadState.file.name);
    } catch (error) {
      setUploadState(prev => ({
        ...prev,
        uploading: false,
        error: error instanceof Error ? error.message : 'Upload failed',
      }));
    }
  }, [uploadState.file]);

  // Navigate to analysis page
  const handleProceedToAnalysis = useCallback(() => {
    window.location.href = '/local/analyze';
  }, []);

  // Reset upload state
  const handleReset = useCallback(() => {
    setUploadState({
      file: null,
      uploading: false,
      uploadProgress: 0,
      error: null,
      success: false,
    });
  }, []);

  return (
    <div className="local-upload-page">
      {/* Header */}
      <header className="upload-header">
        <div className="container">
          <div className="header-content">
            <div className="breadcrumb">
              <a href="/local" className="breadcrumb-link">🧪 Local Development</a>
              <span className="breadcrumb-separator">›</span>
              <span className="breadcrumb-current">📁 File Upload Testing</span>
            </div>
            <h1>Resume File Upload</h1>
            <p className="page-description">
              Test the file upload functionality with drag-and-drop support for resume files.
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="upload-main">
        <div className="container">
          <div className="upload-section">
            <div className="section-header">
              <h2>📤 Upload Your Resume</h2>
              <p>Select your resume file to start the job analysis workflow</p>
            </div>

            <div className="upload-container">
              <FileUpload
                onFileSelect={handleFileSelect}
                onFileRemove={handleFileRemove}
                selectedFile={uploadState.file}
                uploading={uploadState.uploading}
                uploadProgress={uploadState.uploadProgress}
                error={uploadState.error}
                disabled={uploadState.uploading}
              />

              {/* Upload Actions */}
              {uploadState.file && !uploadState.success && (
                <div className="upload-actions">
                  <button
                    className="btn btn-primary"
                    onClick={handleUpload}
                    disabled={uploadState.uploading}
                  >
                    {uploadState.uploading ? (
                      <>
                        <span className="btn-spinner">⏳</span>
                        Uploading... {Math.round(uploadState.uploadProgress)}%
                      </>
                    ) : (
                      <>
                        <span className="btn-icon">📤</span>
                        Upload Resume
                      </>
                    )}
                  </button>
                  
                  <button
                    className="btn btn-outline"
                    onClick={handleFileRemove}
                    disabled={uploadState.uploading}
                  >
                    <span className="btn-icon">🗑️</span>
                    Cancel
                  </button>
                </div>
              )}

              {/* Success State */}
              {uploadState.success && (
                <div className="upload-success">
                  <div className="success-content">
                    <div className="success-icon">✅</div>
                    <h3>Upload Successful!</h3>
                    <p>Your resume has been uploaded and is ready for analysis.</p>
                    
                    <div className="file-summary">
                      <div className="summary-item">
                        <span className="summary-label">File:</span>
                        <span className="summary-value">{uploadState.file?.name}</span>
                      </div>
                      <div className="summary-item">
                        <span className="summary-label">Size:</span>
                        <span className="summary-value">
                          {uploadState.file ? Math.round(uploadState.file.size / 1024) : 0} KB
                        </span>
                      </div>
                      <div className="summary-item">
                        <span className="summary-label">Type:</span>
                        <span className="summary-value">{uploadState.file?.type || 'Unknown'}</span>
                      </div>
                    </div>
                    
                    <div className="success-actions">
                      <button
                        className="btn btn-primary"
                        onClick={handleProceedToAnalysis}
                      >
                        <span className="btn-icon">🚀</span>
                        Start Job Analysis
                      </button>
                      
                      <button
                        className="btn btn-secondary"
                        onClick={handleReset}
                      >
                        <span className="btn-icon">🔄</span>
                        Upload Another File
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Development Info */}
          <div className="dev-info-section">
            <h3>🔧 Development Information</h3>
            
            <div className="info-grid">
              <div className="info-card">
                <h4>📋 Supported Formats</h4>
                <ul>
                  <li>PDF documents (.pdf)</li>
                  <li>Word documents (.docx, .doc)</li>
                  <li>Text files (.txt)</li>
                </ul>
              </div>
              
              <div className="info-card">
                <h4>⚙️ File Validation</h4>
                <ul>
                  <li>Maximum size: 10MB</li>
                  <li>File type validation</li>
                  <li>Content security checks</li>
                </ul>
              </div>
              
              <div className="info-card">
                <h4>🔄 Upload Process</h4>
                <ul>
                  <li>Drag-and-drop support</li>
                  <li>Progress tracking</li>
                  <li>Error handling</li>
                  <li>File preview</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Testing Notes */}
          <div className="testing-notes">
            <h3>📝 Testing Notes</h3>
            <div className="notes-content">
              <div className="note-item">
                <strong>Current Status:</strong> File upload component implemented with full validation
              </div>
              <div className="note-item">
                <strong>Next Steps:</strong> Integration with backend API for real file processing
              </div>
              <div className="note-item">
                <strong>Features:</strong> Drag-and-drop, progress tracking, error handling, file preview
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="upload-footer">
        <div className="container">
          <div className="footer-content">
            <p>&copy; 2025 Kari Pikkarainen. CareerCraft AI - Local Development</p>
            <div className="footer-links">
              <a href="/local" className="footer-link">← Back to Development</a>
              <a href="/local/analyze" className="footer-link">Job Analysis →</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LocalFileUploadPage;