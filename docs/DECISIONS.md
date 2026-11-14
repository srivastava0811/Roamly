# Architecture Decision Records (ADRs)

> **Document Status**: Active / Accepted
> **Project**: Roamly AI Travel Operating System

---

### ADR-001: Monorepo with Turborepo & pnpm Workspaces
- **Status**: Accepted
- **Context**: The project consists of two frontend client shells (Web and Mobile), a shared Python backend, and multiple shared TypeScript libraries (types, tokens, utils, api-client).
- **Decision**: Adopt a unified monorepo powered by `pnpm workspaces` and `Turborepo`.
- **Consequences**:
  - *Positive*: Atomic commits across shared types and consumers; shared dependency caching; unified linting and typechecking via `turbo typecheck`.
  - *Tradeoff*: Python backend sits alongside TypeScript packages. Addressed by isolating `apps/api` with its own virtual environment and pytest runner.

---

### ADR-002: Next.js App Router for Web Frontend
- **Status**: Accepted
- **Context**: The web application requires high search-engine discoverability for travel content, fast initial page loads, and seamless client-side interactivity.
- **Decision**: Use Next.js 15 with App Router, React Server Components (RSC), and Tailwind CSS.
- **Consequences**:
  - *Positive*: Static landing pages and SEO-friendly destination guides render server-side; dynamic dashboard and interactive itineraries run client-side.
  - *Tradeoff*: Server Component vs Client Component boundary discipline required.

---

### ADR-003: React Native with Expo Router for Mobile
- **Status**: Accepted
- **Context**: Native iOS and Android experiences are required while sharing business logic and UI tokens with web without maintaining separate Swift/Kotlin codebases.
- **Decision**: Use React Native with Expo SDK 52+ and Expo Router for file-based navigation.
- **Consequences**:
  - *Positive*: Near 100% code reuse for data types, API client, currency math, and design tokens. File-based routing mirrors Next.js App Router.
  - *Tradeoff*: Certain native modules require Expo prebuild if custom native pods are introduced.

---

### ADR-004: FastAPI with Pydantic v2 & SQLAlchemy 2 for Backend
- **Status**: Accepted
- **Context**: The backend needs asynchronous high-concurrency API handling, native Python AI/agent ecosystem integration (LangGraph, Gemini), and automatic OpenAPI documentation.
- **Decision**: Build the backend using FastAPI with Pydantic v2 schemas and SQLAlchemy 2.0 async ORM.
- **Consequences**:
  - *Positive*: Automatic OpenAPI 3.1 generation powers the TypeScript client generator; native async I/O handles Server-Sent Events; Pydantic v2 provides high-speed C-extension validation.
  - *Tradeoff*: Async SQLAlchemy requires disciplined session lifecycle management via dependency injection (`get_db`).

---

### ADR-005: Supabase PostgreSQL & Auth for Infrastructure
- **Status**: Accepted
- **Context**: External budget is capped at $40–$60 total. Hosting dedicated PostgreSQL clusters, Redis instances, and custom OAuth infrastructure is financially prohibitive.
- **Decision**: Standardize on Supabase for managed PostgreSQL, Supabase Auth, and Supabase Realtime.
- **Consequences**:
  - *Positive*: Generous developer free tier ($0/month); built-in Row-Level Security (RLS); instant JWT verification; Realtime WebSocket channels for group collaboration.
  - *Tradeoff*: Supabase projects auto-pause after 7 days of inactivity during idle development; mitigated by periodic health ping.

---

### ADR-006: OpenAPI as the Sole Authoritative Contract
- **Status**: Accepted
- **Context**: Frontends and backend must not drift out of sync. Breaking API changes must be caught at compile time.
- **Decision**: FastAPI's OpenAPI specification is the single source of truth. TypeScript client code in `packages/api-client` is generated directly from this contract.
- **Consequences**:
  - *Positive*: Eliminates manual TypeScript API interface authoring. If backend modifies an endpoint, running `pnpm run typecheck` immediately highlights broken client components.
  - *Tradeoff*: Requires running `scripts/generate-client.mjs` upon backend route or schema modifications.

---

### ADR-007: Strictly Deterministic Budgeting Engine
- **Status**: Accepted
- **Context**: Large Language Models are probabilistic and prone to arithmetic hallucination, rounding errors, and inconsistency when summing currency amounts.
- **Decision**: LLMs are forbidden from performing arithmetic or budget calculations. All financial logic is computed via deterministic integer-cent arithmetic in `BudgetService` (backend) and `@roamly/shared-utils` (frontend).
- **Consequences**:
  - *Positive*: Guaranteed mathematical precision; eliminates floating point errors (e.g. `0.1 + 0.2 = 0.30000000000000004`); verified by deterministic SHA-256 checksums.
  - *Tradeoff*: Cognitive agents must output structured numbers into tools rather than free-form financial calculations.

---

### ADR-008: LangGraph State Machine for Multi-Agent Orchestration
- **Status**: Accepted
- **Context**: 8 logical agents must collaborate on trip planning with visible progress, step-by-step telemetry, and localized replanning.
- **Decision**: Orchestrate agents using LangGraph's typed StateGraph over `TravelPlanState`.
- **Consequences**:
  - *Positive*: Explicit dependency graphs; persistence of intermediate checkpoints; support for human-in-the-loop approvals; dependency-aware partial replanning.
  - *Tradeoff*: Requires careful state schema versioning across agent upgrades.

---

### ADR-009: Free-Tier Provider Gateway with Mock Fixture Fallbacks
- **Status**: Accepted
- **Context**: Production travel APIs (Amadeus, Google Maps, Sabre) carry high subscription and per-call costs exceeding the $60 lifetime budget.
- **Decision**: Implement a provider gateway prioritizing free open-source services (Open-Meteo, Nominatim, MapLibre, OSRM) with seamless fallback to offline mock fixtures.
- **Consequences**:
  - *Positive*: Zero cloud bills incurred during development; platform remains fully functional offline and in sandboxed CI environments; provenance metadata clearly identifies data origin.
  - *Tradeoff*: Mock flight schedules require explicit UI disclosure to avoid misleading users.

---

### ADR-010: Zero Client-Side Secret Keys Architecture
- **Status**: Accepted
- **Context**: Client applications are delivered to user devices (browsers and smartphones) where any bundled API secret can be decompiled or extracted.
- **Decision**: Frontends never hold LLM API keys (`GEMINI_API_KEY`) or Supabase service role keys. All intelligence, AI inference, and provider integrations run strictly behind FastAPI.
- **Consequences**:
  - *Positive*: Complete defense against credential theft, quota hijacking, and unauthorized billing.
  - *Tradeoff*: All client interactions with AI agents must route through the FastAPI gateway via REST and SSE.

---

## 4. Open Architecture Questions

1. **Vector Storage**: Should semantic destination search use `pgvector` inside the existing Supabase PostgreSQL instance, or can keyword search + LLM reranking suffice for Milestone 1?
   - *Current Recommendation*: Use keyword + metadata filtering first to preserve database resources.
2. **Offline Mobile Cache**: What strategy should Expo mobile use for offline trip view access when traveling without mobile data?
   - *Current Recommendation*: SQLite via `expo-sqlite` or WatermelonDB caching the latest `TripRevision` snapshot.
