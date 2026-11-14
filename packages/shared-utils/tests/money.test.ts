import { describe, it, expect } from 'vitest';
import { addMoney, subtractMoney, toCents, fromCents, formatMoney } from '../src/money';

describe('money utilities (deterministic arithmetic)', () => {
  it('correctly converts to and from cents without floating point errors', () => {
    expect(toCents(19.99)).toBe(1999);
    expect(fromCents(1999)).toBe(19.99);
    // Floating point precision test: 0.1 + 0.2
    expect(fromCents(toCents(0.1) + toCents(0.2))).toBe(0.3);
  });

  it('adds money values with the same currency', () => {
    const a = { amount: 150.25, currency: 'USD' };
    const b = { amount: 49.75, currency: 'USD' };
    const result = addMoney(a, b);
    expect(result.amount).toBe(200.0);
    expect(result.currency).toBe('USD');
  });

  it('subtracts money values correctly', () => {
    const a = { amount: 500.0, currency: 'USD' };
    const b = { amount: 123.45, currency: 'USD' };
    const result = subtractMoney(a, b);
    expect(result.amount).toBe(376.55);
  });

  it('throws an error on mismatched currencies', () => {
    const usd = { amount: 100, currency: 'USD' };
    const eur = { amount: 100, currency: 'EUR' };
    expect(() => addMoney(usd, eur)).toThrow('Cannot add mismatched currencies');
    expect(() => subtractMoney(usd, eur)).toThrow('Cannot subtract mismatched currencies');
  });

  it('formats money for display', () => {
    const m = { amount: 1250.5, currency: 'USD' };
    const formatted = formatMoney(m, 'en-US');
    expect(formatted).toContain('$1,250.50');
  });
});
