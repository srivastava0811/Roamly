import * as React from 'react';
import { cn } from '@/lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'success';
}

export function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  const variantClasses = {
    default: 'border-transparent bg-emerald-600 text-white',
    secondary: 'border-transparent bg-neutral-100 text-neutral-900',
    destructive: 'border-transparent bg-red-600 text-white',
    outline: 'text-neutral-900 border-neutral-300',
    success: 'border-transparent bg-emerald-100 text-emerald-800',
  }[variant];

  return (
    <div
      className={cn(
        'inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
        variantClasses,
        className
      )}
      {...props}
    />
  );
}
