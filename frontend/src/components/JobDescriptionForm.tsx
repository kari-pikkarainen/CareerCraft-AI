/**
 * Job Description Input Form with Validation
 * Comprehensive form for job posting details and analysis input
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import './JobDescriptionForm.css';

interface JobDescriptionData {
  jobTitle: string;
  companyName: string;
  jobDescription: string;
  jobUrl?: string;
  location?: string;
  employmentType?: string;
  experienceLevel?: string;
  salary?: string;
}

interface ValidationErrors {
  jobTitle?: string;
  companyName?: string;
  jobDescription?: string;
  jobUrl?: string;
}

interface ValidationRule {
  required: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
}

interface JobDescriptionFormProps {
  onSubmit: (data: JobDescriptionData) => void;
  onSave?: (data: JobDescriptionData) => void;
  initialData?: Partial<JobDescriptionData>;
  loading?: boolean;
  disabled?: boolean;
  showOptionalFields?: boolean;
}

const JobDescriptionForm: React.FC<JobDescriptionFormProps> = ({
  onSubmit,
  onSave,
  initialData = {},
  loading = false,
  disabled = false,
  showOptionalFields = false,
}) => {
  const [formData, setFormData] = useState<JobDescriptionData>({
    jobTitle: initialData.jobTitle || '',
    companyName: initialData.companyName || '',
    jobDescription: initialData.jobDescription || '',
    jobUrl: initialData.jobUrl || '',
    location: initialData.location || '',
    employmentType: initialData.employmentType || '',
    experienceLevel: initialData.experienceLevel || '',
    salary: initialData.salary || '',
  });

  const [errors, setErrors] = useState<ValidationErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [characterCount, setCharacterCount] = useState(0);
  const [showOptional, setShowOptional] = useState(showOptionalFields);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Validation constraints
  const VALIDATION_RULES: Record<keyof ValidationErrors, ValidationRule> = {
    jobTitle: { required: true, minLength: 2, maxLength: 100 },
    companyName: { required: true, minLength: 2, maxLength: 100 },
    jobDescription: { required: true, minLength: 50, maxLength: 10000 },
    jobUrl: { required: false, pattern: /^https?:\/\/.+/ },
  };

  // Update character count when job description changes
  useEffect(() => {
    setCharacterCount(formData.jobDescription.length);
  }, [formData.jobDescription]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [formData.jobDescription]);

  // Validate individual field
  const validateField = useCallback((name: keyof ValidationErrors, value: string): string | undefined => {
    const rules = VALIDATION_RULES[name];
    if (!rules) return undefined;

    if (rules.required && !value.trim()) {
      return `${name.replace(/([A-Z])/g, ' $1').toLowerCase()} is required`;
    }

    if (value && rules.minLength && value.length < rules.minLength) {
      return `Must be at least ${rules.minLength} characters`;
    }

    if (value && rules.maxLength && value.length > rules.maxLength) {
      return `Must be no more than ${rules.maxLength} characters`;
    }

    if (value && rules.pattern && !rules.pattern.test(value)) {
      if (name === 'jobUrl') {
        return 'Please enter a valid URL (starting with http:// or https://)';
      }
    }

    return undefined;
  }, []);

  // Validate entire form
  const validateForm = useCallback((): boolean => {
    const newErrors: ValidationErrors = {};
    let isValid = true;

    (Object.keys(VALIDATION_RULES) as Array<keyof ValidationErrors>).forEach(field => {
      const error = validateField(field, formData[field] || '');
      if (error) {
        newErrors[field] = error;
        isValid = false;
      }
    });

    setErrors(newErrors);
    return isValid;
  }, [formData, validateField]);

  // Handle input change
  const handleInputChange = useCallback((field: keyof JobDescriptionData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    if (errors[field as keyof ValidationErrors]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  }, [errors]);

  // Handle input blur (for validation)
  const handleInputBlur = useCallback((field: keyof ValidationErrors) => {
    setTouched(prev => ({ ...prev, [field]: true }));
    const error = validateField(field, formData[field] || '');
    setErrors(prev => ({ ...prev, [field]: error }));
  }, [formData, validateField]);

  // Handle form submission
  const handleSubmit = useCallback((event: React.FormEvent) => {
    event.preventDefault();
    
    // Mark all fields as touched
    const allFields = Object.keys(VALIDATION_RULES);
    setTouched(Object.fromEntries(allFields.map(field => [field, true])));
    
    if (validateForm()) {
      onSubmit(formData);
    }
  }, [formData, validateForm, onSubmit]);

  // Handle save draft
  const handleSave = useCallback(() => {
    if (onSave) {
      onSave(formData);
    }
  }, [formData, onSave]);

  // Handle paste from clipboard (for job descriptions)
  const handlePaste = useCallback(async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text && text.length > 50) {
        handleInputChange('jobDescription', text);
      }
    } catch (error) {
      console.warn('Failed to read clipboard:', error);
    }
  }, [handleInputChange]);

  // Clear form
  const handleClear = useCallback(() => {
    setFormData({
      jobTitle: '',
      companyName: '',
      jobDescription: '',
      jobUrl: '',
      location: '',
      employmentType: '',
      experienceLevel: '',
      salary: '',
    });
    setErrors({});
    setTouched({});
    setCharacterCount(0);
  }, []);

  const getFieldError = (field: keyof ValidationErrors) => {
    return touched[field] && errors[field];
  };

  const isFieldValid = (field: keyof ValidationErrors) => {
    return touched[field] && !errors[field] && formData[field];
  };

  return (
    <div className="job-form-container">
      <form onSubmit={handleSubmit} className="job-description-form" noValidate>
        {/* Form Header */}
        <div className="form-header">
          <h3>📋 Job Description Details</h3>
          <p>Provide the job details for comprehensive analysis</p>
        </div>

        {/* Required Fields */}
        <div className="form-section">
          <h4>Required Information</h4>
          
          {/* Job Title */}
          <div className={`form-field ${getFieldError('jobTitle') ? 'error' : ''} ${isFieldValid('jobTitle') ? 'valid' : ''}`}>
            <label htmlFor="jobTitle">
              Job Title *
              <span className="field-hint">Position you're applying for</span>
            </label>
            <input
              id="jobTitle"
              type="text"
              value={formData.jobTitle}
              onChange={(e) => handleInputChange('jobTitle', e.target.value)}
              onBlur={() => handleInputBlur('jobTitle')}
              placeholder="e.g., Senior Software Engineer"
              disabled={disabled || loading}
              maxLength={VALIDATION_RULES.jobTitle.maxLength || 100}
            />
            {getFieldError('jobTitle') && (
              <span className="error-message">{getFieldError('jobTitle')}</span>
            )}
          </div>

          {/* Company Name */}
          <div className={`form-field ${getFieldError('companyName') ? 'error' : ''} ${isFieldValid('companyName') ? 'valid' : ''}`}>
            <label htmlFor="companyName">
              Company Name *
              <span className="field-hint">Organization you're applying to</span>
            </label>
            <input
              id="companyName"
              type="text"
              value={formData.companyName}
              onChange={(e) => handleInputChange('companyName', e.target.value)}
              onBlur={() => handleInputBlur('companyName')}
              placeholder="e.g., Google, Microsoft, Startup Inc."
              disabled={disabled || loading}
              maxLength={VALIDATION_RULES.companyName.maxLength || 100}
            />
            {getFieldError('companyName') && (
              <span className="error-message">{getFieldError('companyName')}</span>
            )}
          </div>

          {/* Job Description */}
          <div className={`form-field textarea-field ${getFieldError('jobDescription') ? 'error' : ''} ${isFieldValid('jobDescription') ? 'valid' : ''}`}>
            <label htmlFor="jobDescription">
              Job Description *
              <span className="field-hint">Complete job posting text</span>
            </label>
            <div className="textarea-wrapper">
              <textarea
                ref={textareaRef}
                id="jobDescription"
                value={formData.jobDescription}
                onChange={(e) => handleInputChange('jobDescription', e.target.value)}
                onBlur={() => handleInputBlur('jobDescription')}
                placeholder="Paste the complete job description here including requirements, responsibilities, qualifications, etc."
                disabled={disabled || loading}
                maxLength={VALIDATION_RULES.jobDescription.maxLength || 10000}
                rows={8}
              />
              <div className="textarea-actions">
                <button
                  type="button"
                  className="btn-paste"
                  onClick={handlePaste}
                  disabled={disabled || loading}
                  title="Paste from clipboard"
                >
                  📋 Paste
                </button>
              </div>
            </div>
            <div className="character-count">
              <span className={characterCount < (VALIDATION_RULES.jobDescription.minLength || 0) ? 'insufficient' : 'sufficient'}>
                {characterCount} / {VALIDATION_RULES.jobDescription.maxLength || 10000} characters
              </span>
              {characterCount < (VALIDATION_RULES.jobDescription.minLength || 0) && (
                <span className="count-hint">
                  (minimum {VALIDATION_RULES.jobDescription.minLength || 0} characters)
                </span>
              )}
            </div>
            {getFieldError('jobDescription') && (
              <span className="error-message">{getFieldError('jobDescription')}</span>
            )}
          </div>
        </div>

        {/* Optional Fields */}
        <div className="form-section">
          <div className="section-toggle">
            <h4>Additional Information</h4>
            <button
              type="button"
              className="toggle-btn"
              onClick={() => setShowOptional(!showOptional)}
              disabled={disabled || loading}
            >
              {showOptional ? '− Hide Optional Fields' : '+ Show Optional Fields'}
            </button>
          </div>

          {showOptional && (
            <div className="optional-fields">
              {/* Job URL */}
              <div className={`form-field ${getFieldError('jobUrl') ? 'error' : ''} ${isFieldValid('jobUrl') ? 'valid' : ''}`}>
                <label htmlFor="jobUrl">
                  Job Posting URL
                  <span className="field-hint">Link to the original job posting</span>
                </label>
                <input
                  id="jobUrl"
                  type="url"
                  value={formData.jobUrl}
                  onChange={(e) => handleInputChange('jobUrl', e.target.value)}
                  onBlur={() => handleInputBlur('jobUrl')}
                  placeholder="https://company.com/careers/job-id"
                  disabled={disabled || loading}
                />
                {getFieldError('jobUrl') && (
                  <span className="error-message">{getFieldError('jobUrl')}</span>
                )}
              </div>

              {/* Location */}
              <div className="form-field">
                <label htmlFor="location">
                  Location
                  <span className="field-hint">Job location or remote</span>
                </label>
                <input
                  id="location"
                  type="text"
                  value={formData.location}
                  onChange={(e) => handleInputChange('location', e.target.value)}
                  placeholder="e.g., San Francisco, CA or Remote"
                  disabled={disabled || loading}
                />
              </div>

              {/* Employment Type */}
              <div className="form-field">
                <label htmlFor="employmentType">
                  Employment Type
                  <span className="field-hint">Full-time, part-time, contract, etc.</span>
                </label>
                <select
                  id="employmentType"
                  value={formData.employmentType}
                  onChange={(e) => handleInputChange('employmentType', e.target.value)}
                  disabled={disabled || loading}
                >
                  <option value="">Select employment type</option>
                  <option value="Full-time">Full-time</option>
                  <option value="Part-time">Part-time</option>
                  <option value="Contract">Contract</option>
                  <option value="Freelance">Freelance</option>
                  <option value="Internship">Internship</option>
                  <option value="Temporary">Temporary</option>
                </select>
              </div>

              {/* Experience Level */}
              <div className="form-field">
                <label htmlFor="experienceLevel">
                  Experience Level
                  <span className="field-hint">Required experience level</span>
                </label>
                <select
                  id="experienceLevel"
                  value={formData.experienceLevel}
                  onChange={(e) => handleInputChange('experienceLevel', e.target.value)}
                  disabled={disabled || loading}
                >
                  <option value="">Select experience level</option>
                  <option value="Entry Level">Entry Level (0-2 years)</option>
                  <option value="Mid Level">Mid Level (2-5 years)</option>
                  <option value="Senior Level">Senior Level (5-8 years)</option>
                  <option value="Lead Level">Lead Level (8-12 years)</option>
                  <option value="Executive Level">Executive Level (12+ years)</option>
                </select>
              </div>

              {/* Salary */}
              <div className="form-field">
                <label htmlFor="salary">
                  Salary Range
                  <span className="field-hint">Compensation information</span>
                </label>
                <input
                  id="salary"
                  type="text"
                  value={formData.salary}
                  onChange={(e) => handleInputChange('salary', e.target.value)}
                  placeholder="e.g., $80,000 - $120,000 or Competitive"
                  disabled={disabled || loading}
                />
              </div>
            </div>
          )}
        </div>

        {/* Form Actions */}
        <div className="form-actions">
          <div className="primary-actions">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={disabled || loading || Object.keys(errors).some(key => errors[key as keyof ValidationErrors])}
            >
              {loading ? (
                <>
                  <span className="btn-spinner">⏳</span>
                  Analyzing...
                </>
              ) : (
                <>
                  <span className="btn-icon">🚀</span>
                  Start Analysis
                </>
              )}
            </button>

            {onSave && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleSave}
                disabled={disabled || loading}
              >
                <span className="btn-icon">💾</span>
                Save Draft
              </button>
            )}
          </div>

          <div className="secondary-actions">
            <button
              type="button"
              className="btn btn-outline"
              onClick={handleClear}
              disabled={disabled || loading}
            >
              <span className="btn-icon">🗑️</span>
              Clear Form
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default JobDescriptionForm;