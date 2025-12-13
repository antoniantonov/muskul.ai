import { describe, it, expect } from 'vitest';
import { formatDate, formatDuration, formatDistance } from '@/utils/format';

describe('format utilities', () => {
  describe('formatDate', () => {
    it('formats date string correctly', () => {
      const date = '2024-01-15T10:00:00Z';
      const formatted = formatDate(date);
      expect(formatted).toContain('January');
      expect(formatted).toContain('15');
      expect(formatted).toContain('2024');
    });

    it('formats Date object correctly', () => {
      const date = new Date('2024-01-15T10:00:00Z');
      const formatted = formatDate(date);
      expect(formatted).toContain('January');
      expect(formatted).toContain('15');
      expect(formatted).toContain('2024');
    });
  });

  describe('formatDuration', () => {
    it('formats seconds only', () => {
      expect(formatDuration(45)).toBe('45s');
    });

    it('formats minutes and seconds', () => {
      expect(formatDuration(125)).toBe('2m 5s');
    });

    it('formats hours and minutes', () => {
      expect(formatDuration(5400)).toBe('1h 30m');
    });
  });

  describe('formatDistance', () => {
    it('formats meters when less than 1000', () => {
      expect(formatDistance(500)).toBe('500 m');
    });

    it('formats kilometers when 1000 or more', () => {
      expect(formatDistance(5000)).toBe('5.00 km');
    });

    it('formats kilometers with decimals', () => {
      expect(formatDistance(5250)).toBe('5.25 km');
    });
  });
});
