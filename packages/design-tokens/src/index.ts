import { colors } from './colors';
import { typography } from './typography';
import { spacing, radii, shadows } from './spacing';

export * from './colors';
export * from './typography';
export * from './spacing';

export const designTokens = {
  colors,
  typography,
  spacing,
  radii,
  shadows,
} as const;

export type DesignTokens = typeof designTokens;
