import { Money } from '@roamly/shared-types';

/**
 * Converts a decimal dollar/euro amount to integer cents to avoid IEEE 754 floating-point errors.
 */
export function toCents(amount: number): number {
  return Math.round(amount * 100);
}

/**
 * Converts integer cents back to a 2-decimal number.
 */
export function fromCents(cents: number): number {
  return cents / 100;
}

/**
 * Adds two Money objects with currency validation.
 */
export function addMoney(a: Money, b: Money): Money {
  if (a.currency !== b.currency) {
    throw new Error(`Cannot add mismatched currencies: ${a.currency} and ${b.currency}`);
  }
  const totalCents = toCents(a.amount) + toCents(b.amount);
  return {
    amount: fromCents(totalCents),
    currency: a.currency,
  };
}

/**
 * Subtracts Money b from Money a with currency validation.
 */
export function subtractMoney(a: Money, b: Money): Money {
  if (a.currency !== b.currency) {
    throw new Error(`Cannot subtract mismatched currencies: ${a.currency} and ${b.currency}`);
  }
  const remainingCents = toCents(a.amount) - toCents(b.amount);
  return {
    amount: fromCents(remainingCents),
    currency: a.currency,
  };
}

/**
 * Formats a Money object for UI display using Intl.NumberFormat.
 */
export function formatMoney(money: Money, locale: string = 'en-US'): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: money.currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(money.amount);
}
