export const colors = {
  // Brand palette
  brand: {
    50: '#F0FDF4',
    100: '#DCFCE7',
    200: '#BBF7D0',
    300: '#86EFAC',
    400: '#4ADE80',
    500: '#22C55E', // Primary Roamly Emerald
    600: '#16A34A',
    700: '#15803D',
    800: '#166534',
    900: '#14532D',
    950: '#052E16',
  },
  // Accent palette (warm adventure ochre/amber)
  accent: {
    50: '#FFFBEB',
    100: '#FEF3C7',
    200: '#FDE68A',
    300: '#FCD34D',
    400: '#FBBF24',
    500: '#F59E0B',
    600: '#D97706',
    700: '#B45309',
    800: '#92400E',
    900: '#78350F',
  },
  // Neutrals / Slate
  neutral: {
    50: '#F8FAFC',
    100: '#F1F5F9',
    200: '#E2E8F0',
    300: '#CBD5E1',
    400: '#94A3B8',
    500: '#64748B',
    600: '#475569',
    700: '#334155',
    800: '#1E293B',
    900: '#0F172A',
    950: '#020617',
  },
  // Semantic status
  semantic: {
    success: '#16A34A',
    warning: '#D97706',
    error: '#DC2626',
    info: '#2563EB',
  },
  // Surface and text tokens
  light: {
    background: '#FFFFFF',
    foreground: '#0F172A',
    surface: '#F8FAFC',
    surfaceRaised: '#FFFFFF',
    border: '#E2E8F0',
    mutedText: '#64748B',
  },
  dark: {
    background: '#0B0F19',
    foreground: '#F8FAFC',
    surface: '#111827',
    surfaceRaised: '#1E293B',
    border: '#334155',
    mutedText: '#94A3B8',
  },
} as const;
