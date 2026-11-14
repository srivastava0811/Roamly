# Roamly — Autonomous AI Travel Operating System

<div align="center">

[![CI](https://github.com/roamly/roamly/actions/workflows/ci.yml/badge.svg)](https://github.com/roamly/roamly/actions/workflows/ci.yml)
[![Turborepo](https://img.shields.io/badge/Turborepo-2.x-EF4444.svg)](https://turbo.build/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15.x-000000.svg)](https://nextjs.org/)
[![Expo](https://img.shields.io/badge/Expo-52.x-000020.svg)](https://expo.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6.svg)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://www.python.org/)

**Production-oriented cross-platform AI travel operating system monorepo.**
*Target Release Milestone: December 15, 2026*

</div>

---

## 1. Product Vision

Roamly is an intelligent travel operating system designed to replace fragmented booking spreadsheets, disconnected apps, and hallucination-prone travel planners.

Key Capabilities:
- **Budget-First Discovery**: Mathematical ceiling exploration. No hallucinated travel costs.
- **Coordinated Agent Graph**: 8 specialized agents communicating through typed shared state with visible execution progress.
- **Deterministic Budget Arithmetic**: Integer-cent financial validation protected by SHA-256 checksums.
- **Dependency-Aware Replanning**: Modifying a date or hotel recalibrates downstream schedules without costly full replanning.
- **Free-First Provider Gateway**: Out-of-the-box support for open-source providers (Open-Meteo, MapLibre, Nominatim, OSRM) with offline mock fallbacks.
- **Unified Cross-Platform Core**: Shared generated TypeScript API client for Next.js Web and Expo Native Mobile.
- **$40–$60 Hard Cost Ceiling**: Engineered for $0 recurring monthly infrastructure during early development.

---

## 2. Monorepo Structure

```text
roamly/
├── apps/
│   ├── api/                     # Python FastAPI Backend Core
│   │   ├── app/
│   │   │   ├── api/v1/          # Versioned REST & SSE Endpoints
│   │   │   ├── agents/          # 8 Logical Agent Definitions & Registry
│   │   │   ├── workflows/       # LangGraph TravelPlanState & Replanning Graph
│   │   │   ├── providers/       # Gateway with Places, Maps, Weather, Flights, Lodging, Transit
│   │   │   ├── services/        # TripService, BudgetService (Deterministic Math)
│   │   │   ├── repositories/    # Async SQLAlchemy 2 Repositories
│   │   │   ├── models/          # Database Models (User, Trip, ItineraryDay, Revision)
│   │   │   ├── schemas/         # Pydantic v2 Contract Schemas
│   │   │   ├── core/            # Configuration, Structured Logging, Custom Exceptions
│   │   │   ├── db/              # Async Engine, Session Lifecycle, Health Check
│   │   │   └── events/          # In-Memory Event Publisher for SSE Streams
│   │   ├── alembic/             # Database Migration Scripts
│   │   ├── tests/               # Pytest Test Suite (Health, Trips, Budget)
│   │   └── requirements.txt     # Python Dependencies
│   ├── web/                     # Next.js 15 App Router Frontend
│   │   ├── src/app/             # Landing Page, Dashboard, Layout, Styling
│   │   ├── src/components/      # SystemStatus, shadcn/ui-compatible primitives
│   │   └── tailwind.config.ts   # Design Tokens Tailwind Theme Extension
│   └── mobile/                  # React Native / Expo Router Cross-Platform Mobile
│       ├── src/app/             # Expo File-Based Navigation (Tabs, Screens)
│       └── app.json             # Expo Configuration
├── packages/
│   ├── api-client/              # Type-Safe API Client (Exported from FastAPI OpenAPI)
│   ├── shared-types/            # Canonical TypeScript Interfaces & Enums
│   ├── shared-utils/            # Deterministic Money Math, Date & Geo Utilities
│   └── design-tokens/           # Universal Design Tokens (Colors, Spacing, Typography)
├── docs/                        # Complete Architectural & Engineering Documentation
│   ├── ARCHITECTURE.md          # Topology, Data Flows, Boundaries, Security
│   ├── API_CONTRACTS.md         # OpenAPI Authority, Error Codes, Generation Policy
│   ├── DATA_MODELS.md           # Proposed Domain Entities, ER Diagram, Revisions
│   ├── AGENT_DESIGN.md          # 8 Logical Agents, LangGraph State, Tool Calling
│   ├── PROVIDER_STRATEGY.md     # Free-First Tiering, Adapters, Provenance Tagging
│   ├── COST_BUDGET.md           # $60 Ceiling Tracking, Free Quotas, Forbidden Spend
│   ├── DEVELOPMENT_ROADMAP.md   # Milestones through December 15, 2026
│   └── DECISIONS.md             # Architecture Decision Records (ADR-001 to ADR-010)
├── scripts/                     # Tooling (OpenAPI export, client generator)
├── .github/workflows/           # GitHub Actions CI Workflow
├── AGENTS.md                    # Multi-Agent Collaboration Protocol & Ownership
├── pnpm-workspace.yaml          # Monorepo Workspace Configuration
├── turbo.json                   # Turborepo Build Pipelines
└── package.json                 # Monorepo Root Scripts & Tools
```

---

## 3. Quickstart & Setup

### Prerequisites
- **Node.js**: `v20.0.0` or higher (verified on v26.13)
- **pnpm**: `v9.0.0` or higher (tested with v12.18)
- **Python**: `3.11` or higher (verified on 3.11.9)

### 1. Install Dependencies
```bash
# Install Node workspace dependencies
pnpm install

# Set up Python backend virtual environment
python -m venv apps/api/.venv

# Activate virtual environment (Windows PowerShell)
.\apps\api\.venv\Scripts\Activate.ps1
# (Or on Linux/macOS: source apps/api/.venv/bin/activate)

# Install Python backend dependencies
pip install -r apps/api/requirements.txt
```

### 2. Environment Variables
Copy the root `.env.example` to `.env` or application-specific directories:
```bash
cp .env.example .env
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env
cp apps/mobile/.env.example apps/mobile/.env
```

---

## 4. Running the Applications

### Start Backend API (FastAPI)
```bash
# Run FastAPI with live reload on http://localhost:8000
cd apps/api
..\..\apps\api\.venv\Scripts\uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Health Check: `http://localhost:8000/health`
- Interactive Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Start Web Application (Next.js)
```bash
# Run Next.js App Router on http://localhost:3000
pnpm --filter @roamly/web dev
```
- Landing Page: `http://localhost:3000`
- Dashboard: `http://localhost:3000/dashboard`

### Start Mobile Application (Expo)
```bash
# Launch Expo dev server on http://localhost:8081
pnpm --filter @roamly/mobile start
```

### Run All Applications Concurrently
```bash
pnpm dev
```

---

## 5. Testing & Verification

| Test Target | Command | Technology |
|---|---|---|
| **Backend API Tests** | `.\apps\api\.venv\Scripts\python -m pytest apps/api/tests -v` | pytest, httpx, aiosqlite |
| **Shared Utils Tests** | `pnpm --filter @roamly/shared-utils test` | Vitest |
| **Monorepo Typecheck** | `pnpm run typecheck` | Turborepo, TypeScript |
| **Web Production Build** | `pnpm --filter @roamly/web build` | Next.js 15 Compiler |
| **Client Regeneration** | `pnpm run generate:client` | Node.js, Python OpenAPI exporter |

---

## 6. Coding Agent Collaboration

AI coding agents and human engineers must adhere strictly to [AGENTS.md](./AGENTS.md):
- **Frontend Agents**: Own `apps/web`, `apps/mobile`, and UI design tokens.
- **Backend Agents**: Own `apps/api`, database models, Alembic migrations, and agent orchestration.
- **Contract Rule**: Never manually edit client types. All changes originate in `apps/api/app/schemas/` and flow through `scripts/generate-client.mjs`.

---

## 7. License & Milestone

- Target Release Milestone: **December 15, 2026**
- Budget Target: **$0 recurring spend / $60 maximum lifetime external budget**
