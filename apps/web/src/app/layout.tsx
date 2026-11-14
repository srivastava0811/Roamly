import type { Metadata } from 'next';
import Link from 'next/link';
import './globals.css';
import { SystemStatus } from '@/components/system-status';
import { Compass } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Roamly | AI-Powered Travel Operating System',
  description: 'Budget-first destination discovery, agentic itinerary planning, and seamless group coordination.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-neutral-50 text-neutral-900 antialiased">
        <header className="sticky top-0 z-50 w-full border-b border-neutral-200 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
          <div className="container mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
            <div className="flex items-center gap-6">
              <Link href="/" className="flex items-center gap-2 font-bold text-xl tracking-tight text-neutral-900">
                <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center text-white shadow-sm">
                  <Compass className="w-5 h-5" />
                </div>
                <span>Roamly</span>
              </Link>
              <nav className="hidden md:flex items-center gap-5 text-sm font-medium text-neutral-600">
                <Link href="/" className="hover:text-emerald-600 transition-colors">
                  Overview
                </Link>
                <Link href="/dashboard" className="hover:text-emerald-600 transition-colors">
                  Dashboard
                </Link>
              </nav>
            </div>
            <div className="flex items-center gap-3">
              <SystemStatus />
            </div>
          </div>
        </header>

        <main className="flex-1">{children}</main>

        <footer className="border-t border-neutral-200 bg-white py-6">
          <div className="container mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between text-xs text-neutral-500 gap-2">
            <div>© 2026 Roamly Operating System. Milestone target: December 15, 2026.</div>
            <div className="flex items-center gap-4">
              <span>Next.js App Router</span>
              <span>FastAPI Gateway</span>
              <span>Supabase</span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
