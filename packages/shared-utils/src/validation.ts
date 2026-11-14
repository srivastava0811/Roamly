/**
 * Validates email format.
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Sanitizes user input titles by trimming and collapsing multiple spaces.
 */
export function sanitizeTitle(title: string): string {
  return title.trim().replace(/\s+/g, ' ');
}
