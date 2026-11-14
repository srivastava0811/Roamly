/**
 * Calculates inclusive day count between two YYYY-MM-DD date strings.
 */
export function calculateDaysBetween(startDate: string, endDate: string): number {
  const start = new Date(startDate);
  const end = new Date(endDate);
  
  if (isNaN(start.getTime()) || isNaN(end.getTime())) {
    throw new Error(`Invalid date string provided: ${startDate} or ${endDate}`);
  }

  const diffTime = end.getTime() - start.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return Math.max(0, diffDays + 1); // Inclusive of both start and end day
}

/**
 * Validates that start is before or equal to end date.
 */
export function isValidDateRange(startDate: string, endDate: string): boolean {
  const start = new Date(startDate);
  const end = new Date(endDate);
  if (isNaN(start.getTime()) || isNaN(end.getTime())) {
    return false;
  }
  return start <= end;
}

/**
 * Formats YYYY-MM-DD into a localized friendly string.
 */
export function formatDateDisplay(isoDate: string, locale: string = 'en-US'): string {
  const date = new Date(isoDate);
  if (isNaN(date.getTime())) return isoDate;
  return new Intl.DateTimeFormat(locale, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(date);
}
