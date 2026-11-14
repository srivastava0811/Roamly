import { describe, it, expect } from 'vitest';
import { calculateDaysBetween, isValidDateRange } from '../src/dates';

describe('date utilities', () => {
  it('calculates inclusive days correctly', () => {
    // 2026-12-01 to 2026-12-05 is 5 days
    expect(calculateDaysBetween('2026-12-01', '2026-12-05')).toBe(5);
    // Same day is 1 day
    expect(calculateDaysBetween('2026-12-01', '2026-12-01')).toBe(1);
  });

  it('validates date ranges', () => {
    expect(isValidDateRange('2026-12-01', '2026-12-10')).toBe(true);
    expect(isValidDateRange('2026-12-10', '2026-12-01')).toBe(false);
    expect(isValidDateRange('invalid', '2026-12-01')).toBe(false);
  });
});
