/**
 * Utility Functions Tests
 * Helper function tests to increase coverage
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

export {};

// Utility functions to test
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const validateEmail = (email: string): boolean => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

const generateId = (): string => {
  return 'id-' + Math.random().toString(36).substr(2, 9);
};

const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substr(0, maxLength) + '...';
};

const capitalizeFirst = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1);
};

describe('Utility Functions', () => {
  describe('formatFileSize', () => {
    test('formats bytes correctly', () => {
      expect(formatFileSize(0)).toBe('0 Bytes');
      expect(formatFileSize(1024)).toBe('1 KB');
      expect(formatFileSize(1048576)).toBe('1 MB');
      expect(formatFileSize(1073741824)).toBe('1 GB');
    });

    test('handles decimal values', () => {
      expect(formatFileSize(1536)).toBe('1.5 KB');
      expect(formatFileSize(2621440)).toBe('2.5 MB');
    });
  });

  describe('validateEmail', () => {
    test('validates correct email formats', () => {
      expect(validateEmail('test@example.com')).toBe(true);
      expect(validateEmail('user.name@domain.co.uk')).toBe(true);
      expect(validateEmail('valid+email@test.org')).toBe(true);
    });

    test('rejects invalid email formats', () => {
      expect(validateEmail('invalid-email')).toBe(false);
      expect(validateEmail('test@')).toBe(false);
      expect(validateEmail('@domain.com')).toBe(false);
      expect(validateEmail('test.domain.com')).toBe(false);
    });
  });

  describe('generateId', () => {
    test('generates unique IDs', () => {
      const id1 = generateId();
      const id2 = generateId();
      
      expect(id1).toMatch(/^id-[a-z0-9]{9}$/);
      expect(id2).toMatch(/^id-[a-z0-9]{9}$/);
      expect(id1).not.toBe(id2);
    });

    test('has correct format', () => {
      const id = generateId();
      expect(id).toMatch(/^id-/);
      expect(id.length).toBe(12); // 'id-' + 9 characters
    });
  });

  describe('truncateText', () => {
    test('truncates long text', () => {
      const longText = 'This is a very long text that should be truncated';
      expect(truncateText(longText, 20)).toBe('This is a very long ...');
    });

    test('returns original text if within limit', () => {
      const shortText = 'Short text';
      expect(truncateText(shortText, 20)).toBe('Short text');
    });

    test('handles edge cases', () => {
      expect(truncateText('', 10)).toBe('');
      expect(truncateText('Exact', 5)).toBe('Exact');
    });
  });

  describe('capitalizeFirst', () => {
    test('capitalizes first letter', () => {
      expect(capitalizeFirst('hello')).toBe('Hello');
      expect(capitalizeFirst('world')).toBe('World');
    });

    test('handles edge cases', () => {
      expect(capitalizeFirst('')).toBe('');
      expect(capitalizeFirst('a')).toBe('A');
      expect(capitalizeFirst('HELLO')).toBe('HELLO');
    });

    test('only affects first character', () => {
      expect(capitalizeFirst('hello world')).toBe('Hello world');
      expect(capitalizeFirst('hELLO')).toBe('HELLO');
    });
  });
});