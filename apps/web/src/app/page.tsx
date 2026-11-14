import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Sparkles,
  DollarSign,
  Compass,
  MapPin,
  Bot,
  Users,
  ShieldCheck,
  ArrowRight,
} from 'lucide-react';

export default function HomePage() {
  return (
    <div className="container mx-auto px-4 sm:px-6 py-12 sm:py-20 flex flex-col items-center">
      {/* Hero Badge */}
      <div className="mb-6 flex items-center gap-2">
        <Badge variant="success" className="px-3 py-1 text-xs uppercase tracking-wider font-semibold">
          Architecture Foundation v0.1.0
        </Badge>
        <span className="text-xs text-neutral-500 font-medium">
          Milestone: December 15, 2026
        </span>
      </div>

      {/* Hero Title & Subtitle */}
      <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-center max-w-4xl text-neutral-900 leading-[1.15]">
        The Intelligent Operating System for{' '}
        <span className="text-emerald-600">Budget-First Travel</span>
      </h1>
      <p className="mt-6 text-lg sm:text-xl text-neutral-600 text-center max-w-2xl leading-relaxed">
        Autonomous coordinated AI agents designed for destination discovery, deterministic budgeting,
        weather-aware logistics, and real-time group collaboration.
      </p>

      {/* Hero CTAs */}
      <div className="mt-8 flex flex-col sm:flex-row items-center gap-4">
        <Link href="/dashboard">
          <Button size="lg" className="gap-2 font-medium">
            Open Planning Dashboard
            <ArrowRight className="w-4 h-4" />
          </Button>
        </Link>
        <a
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Button variant="outline" size="lg" className="gap-2 font-medium">
            Explore FastAPI Swagger
          </Button>
        </a>
      </div>

      {/* Feature Pillar Grid */}
      <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-6xl">
        <Card className="hover:shadow-md transition-shadow">
          <CardHeader>
            <div className="w-10 h-10 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center mb-2">
              <DollarSign className="w-5 h-5" />
            </div>
            <CardTitle>Budget-First Discovery</CardTitle>
            <CardDescription>
              Arithmetic precision over hallucinated costs.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-sm text-neutral-600 leading-relaxed">
            Every itinerary allocation is validated with integer-cent deterministic math. LLMs are never
            trusted with additions or arithmetic checks.
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardHeader>
            <div className="w-10 h-10 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center mb-2">
              <Bot className="w-5 h-5" />
            </div>
            <CardTitle>Coordinated Agent Graph</CardTitle>
            <CardDescription>
              8 specialized agents communicating through typed state.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-sm text-neutral-600 leading-relaxed">
            From Destination Discovery to Weather and Mobility, execution progress streams via Server-Sent
            Events with dependency-aware automatic replanning.
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardHeader>
            <div className="w-10 h-10 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center mb-2">
              <Users className="w-5 h-5" />
            </div>
            <CardTitle>Shared Multi-Platform Core</CardTitle>
            <CardDescription>
              Unified OpenAPI contracts for Web and Expo Mobile.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-sm text-neutral-600 leading-relaxed">
            Zero secret keys on client devices. Strictly typed generated TypeScript client ensuring
            guaranteed cross-platform consistency.
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
