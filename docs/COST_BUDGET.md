# Project Cost Budget & Financial Ceiling

> **Absolute Financial Ceiling**: **$40–$60 total lifetime budget** (NOT recurring monthly).
> **Operating Target**: **$0.00 / month recurring infrastructure cost** during development.
> **Approval Policy**: Automatic billing enablement is strictly prohibited. Every paid service requires explicit written authorization.

---

## 1. Budget Allocation Breakdown

| Component | Provider / Tier | Projected Cost | Hard Ceiling | Notes |
|---|---|---|---|---|
| **Database & Auth** | Supabase Free Tier | $0.00 | $0.00 | 500MB DB, 50,000 monthly active users, 2 projects included in free tier. |
| **Web Hosting** | Vercel Hobby Free Tier | $0.00 | $0.00 | Free for personal/portfolio Next.js deployments. |
| **Backend API Hosting**| Railway / Render Free/Hobby Tier | $0.00 | $10.00 | Free trial / hobby compute credits; local Docker for development. |
| **AI Inference (LLM)** | Google AI Studio / Gemini API Free Tier | $0.00 | $25.00 | Gemini 1.5 Flash offers 15 RPM free tier without billing enabled. |
| **Domain Name (Optional)** | Cloudflare Registrar | $10.00 | $12.00 | `.com` or `.app` registration for December 15 launch milestone. |
| **Contingency Reserve** | Unforeseen developer tools / SMS | $0.00 | $13.00 | Kept in reserve. |
| **TOTAL** | | **$10.00** | **$60.00 MAX** | Guaranteed within the $40–$60 ceiling. |

---

## 2. Free-Tier Dependencies & Quota Ceilings

### 2.1 Google Gemini API
- **Model Choice**: `gemini-1.5-flash` (or current stable equivalent).
- **Free Quota**: 15 requests per minute (RPM), 1,500 requests per day (RPD), 1 million tokens per minute (TPM).
- **Safety Rule**:
  - The API key must never have a credit card linked to automatic pay-as-you-go billing without explicit authorization.
  - If the free tier 15 RPM quota is approached, the backend gateway throttles requests rather than bursting to paid billing.

### 2.2 Supabase
- **Free Quota**: 500MB PostgreSQL storage, 5GB bandwidth, 50,000 MAU.
- **Auto-Pause Awareness**: Free-tier projects pause after 1 week of inactivity. A scheduled health ping script or webhook will keep the staging instance active.

### 2.3 Open-Source & Public APIs
- **Open-Meteo**: 10,000 free calls/day (requires no API key).
- **OpenStreetMap Nominatim**: 1 call/sec max (rate-limited via in-memory token bucket).
- **OSRM Public Server**: Routing demonstration (cached locally).

---

## 3. High-Risk Cost Triggers & Strict Prohibitions

1. **NO Paid Flight GDS APIs**:
   - Production airline booking APIs (Sabre, Travelport, Amadeus Enterprise) cost thousands of dollars per month. Under no circumstances may any agent sign up for paid GDS plans.
   - Development uses `MockFlightsProvider` and free self-service developer sandboxes.
2. **NO Google Maps Platform Pay-As-You-Go**:
   - Google Maps JavaScript API and Places API charge $7–$17 per 1,000 requests after initial credits.
   - Roamly exclusively uses MapLibre GL JS (open source) and Nominatim/Overpass.
3. **NO Paid Vector Databases**:
   - Do not provision Pinecone, Weaviate Cloud, or Qdrant Cloud.
   - If vector search is needed, use `pgvector` inside the free Supabase PostgreSQL instance.
4. **NO Redis Cloud or Kafka**:
   - In-memory Python caching and Supabase Realtime replace external Redis / Kafka clusters.

---

## 4. Expenditure Audit Protocol

Any proposed expenditure against the $40–$60 budget must be logged below:

| Date | Item Description | Amount | Approved By | Cumulative Spend |
|---|---|---|---|---|
| *Pending* | Domain Name Registration (optional) | ~$10.00 | Human Architect | $10.00 / $60.00 |
| *Pending* | Staging API Hosting Buffer | ~$10.00 | Human Architect | $20.00 / $60.00 |
