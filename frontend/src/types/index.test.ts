/**
 * Types Tests
 * Basic type checking and enum tests
 * 
 * CareerCraft AI - Proprietary Software
 * Copyright (c) 2025 Kari Pikkarainen. All rights reserved.
 */

import { ToneEnum, ProcessingStatusEnum, PriorityEnum } from './index';

describe('Enums', () => {
  test('ToneEnum has correct values', () => {
    expect(ToneEnum.PROFESSIONAL).toBe('professional');
    expect(ToneEnum.CONVERSATIONAL).toBe('conversational');
    expect(ToneEnum.ENTHUSIASTIC).toBe('enthusiastic');
    expect(ToneEnum.CONFIDENT).toBe('confident');
  });

  test('ProcessingStatusEnum has correct values', () => {
    expect(ProcessingStatusEnum.PENDING).toBe('pending');
    expect(ProcessingStatusEnum.PROCESSING).toBe('processing');
    expect(ProcessingStatusEnum.COMPLETED).toBe('completed');
    expect(ProcessingStatusEnum.FAILED).toBe('failed');
  });

  test('PriorityEnum has correct values', () => {
    expect(PriorityEnum.LOW).toBe('low');
    expect(PriorityEnum.MEDIUM).toBe('medium');
    expect(PriorityEnum.HIGH).toBe('high');
  });

  test('enum values are strings', () => {
    expect(typeof ToneEnum.PROFESSIONAL).toBe('string');
    expect(typeof ProcessingStatusEnum.PROCESSING).toBe('string');
    expect(typeof PriorityEnum.HIGH).toBe('string');
  });
});