# Agent Design & Orchestration Architecture

> **Orchestrator Framework**: LangGraph (StateGraph)
> **AI Inference Model**: Gemini API (Flash-tier for cost efficiency)
> **Streaming Protocol**: Server-Sent Events (SSE)
> **State Protocol**: Typed, immutable state dictionaries

---

## 1. Architectural Philosophy: Hybrid Multi-Agent Coordination

Not every agent requires an expensive LLM invocation. Roamly employs a **hybrid architecture** where deterministic agents (Budget, Transportation routing, Group voting) use pure algorithmic arithmetic and provider queries, while cognitive agents (Destination Discovery, Itinerary Synthesis, Weather/Wardrobe synthesis) invoke LLMs with structured Pydantic tool schemas.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        Orchestrator Agent                              │
│              (Evaluates Dependencies & Routes Execution)               │
└─────┬──────────────────┬──────────────────┬──────────────────┬─────────┘
      │                  │                  │                  │
      ▼                  ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Destination │    │  Transport  │    │Accommodation│    │  Itinerary  │
│  Discovery  │    │  & Mobility │    │    Agent    │    │  & Routing  │
│ [Cognitive] │    │[Algorithmic]│    │[Algorithmic]│    │ [Cognitive] │
└─────┬───────┘    └─────┬───────┘    └─────┬───────┘    └─────┬───────┘
      │                  │                  │                  │
      └──────────────────┼──────────────────┼──────────────────┘
                         ▼                  ▼
                   ┌─────────────┐    ┌─────────────┐
                   │   Weather   │    │   Budget    │
                   │ & Wardrobe  │    │    Agent    │
                   │ [Cognitive] │    │[Algorithmic]│
                   └─────────────┘    └─────────────┘
```

---

## 2. The 8 Logical Agents

### 1. Orchestrator Agent
- **Type**: Cognitive Router & State Coordinator.
- **Responsibilities**:
  - Ingests user trip criteria and parses intent.
  - Constructs the initial workflow DAG in LangGraph.
  - Monitors intermediate progress events and emits SSE telemetry.
  - Intercepts user revisions and triggers partial downstream replanning.
- **LLM Need**: Low/Moderate. Evaluates plan completion and error recovery.

### 2. Destination Discovery Agent
- **Type**: Cognitive Matching.
- **Responsibilities**:
  - Implements budget-first destination discovery.
  - Searches destination databases given maximum total budget ceiling, traveler interests, and weather preferences.
  - Synthesizes comparative tradeoffs (e.g. "Kyoto in November: gorgeous foliage, moderate crowds, fits within $3,500 total budget").
- **LLM Need**: Yes (Structured Gemini generation).

### 3. Transportation and Mobility Agent
- **Type**: Algorithmic & Provider Lookup.
- **Responsibilities**:
  - Evaluates inter-city travel (flights, long-distance trains, driving routes).
  - Queries provider adapters (or mock fixtures) for real-time fares and schedule feasibility.
  - Calculates carbon emission estimates and local transit connectivity.
- **LLM Need**: No. Pure provider integration and deterministic route scoring.

### 4. Accommodation Agent
- **Type**: Algorithmic & Geo-Spatial Filter.
- **Responsibilities**:
  - Discovers hotels, hostels, and vacation rentals within proximity to planned activity clusters.
  - Filters properties by price ceiling, required amenities (Wi-Fi, elevator), and guest count.
  - Evaluates neighborhood safety, walkability, and transit accessibility.
- **LLM Need**: No. Database query and provider scoring.

### 5. Itinerary and Routing Agent
- **Type**: Cognitive Synthesis with Geo-Optimization.
- **Responsibilities**:
  - Sequences daily activities to minimize inter-venue transit time (traveling salesperson optimization).
  - Respects venue opening hours, pacing preferences (relaxed vs. fast-paced), and meal schedules.
  - Produces structured daily timelines with coordinates and duration estimates.
- **LLM Need**: Yes (Gemini tool-assisted sequencing).

### 6. Budget Agent
- **Type**: Strictly Deterministic.
- **Responsibilities**:
  - Performs integer-cent arithmetic for all allocations, estimates, and expenses.
  - Evaluates category ratios (transportation, lodging, activities, dining, contingency).
  - Flags budget overrun warnings before commitments are finalized.
  - Calculates deterministic SHA-256 integrity checksums.
- **LLM Need**: STRICTLY FORBIDDEN. Zero LLM calculations.

### 7. Weather and Wardrobe Agent
- **Type**: Cognitive Synthesis from Real Forecasts.
- **Responsibilities**:
  - Fetches seasonal averages or live multi-day forecasts via Open-Meteo.
  - Synthesizes temperature ranges, rain probabilities, and UV index.
  - Generates context-aware packing lists and daily outfit recommendations tailored to planned activities (e.g. temple dress codes, hiking gear).
- **LLM Need**: Yes (Gemini synthesis of raw weather metrics into packing advice).

### 8. Group Coordination Agent
- **Type**: Algorithmic Voting & Consensus.
- **Responsibilities**:
  - Gathers individual votes and preferences across group members.
  - Executes quadratic voting or consensus-scoring algorithms on conflicting activities.
  - Highlights deadlocks and proposes balanced compromises.
- **LLM Need**: No (Algorithmic consensus logic).

---

## 3. Shared State Schema (`TravelPlanState`)

All agents read from and mutate a typed dictionary in LangGraph:

```python
class TravelPlanState(TypedDict, total=False):
    trip_id: str
    revision_id: str
    user_id: str
    title: str
    origin_city: Optional[str]
    destination_city: str
    destination_country: str
    start_date: str
    end_date: str
    party_size: int
    total_budget: float
    currency: str
    preferences: Dict[str, Any]

    # Partial updates returned by agents
    discovered_destinations: List[Dict[str, Any]]
    transportation_options: List[Dict[str, Any]]
    selected_transportation: Optional[Dict[str, Any]]
    accommodation_options: List[Dict[str, Any]]
    selected_accommodation: Optional[Dict[str, Any]]
    itinerary_days: List[Dict[str, Any]]
    budget_breakdown: Optional[Dict[str, Any]]
    weather_summary: List[Dict[str, Any]]
    packing_list: List[str]

    # Execution telemetry
    active_agent: Optional[AgentRole]
    completed_agents: List[AgentRole]
    replanning_needed: bool
    replan_reason: Optional[str]
```

---

## 4. Dependency-Aware Automatic Replanning

When a user modifies a parameter, Roamly does NOT wipe the itinerary and run a full, costly multi-agent workflow. The `ReplanningDependencyGraph` calculates minimal invalidation:

| Field Changed | Invalidated Downstream Agents | Actions Taken |
|---|---|---|
| **Dates** | Transport, Accommodation, Itinerary, Weather, Budget | Updates flight/hotel dates; queries new weather forecasts; adjusts daily schedules. |
| **Destination** | All Downstream Agents | Full replan required. |
| **Party Size** | Accommodation, Transport, Budget | Recomputes room counts, vehicle capacities, and per-person cost shares. |
| **Total Budget** | Budget Agent | Rebalances category allocation buckets; flags warnings if existing selections exceed new cap. |
| **Hotel Selection** | Itinerary Routing | Daily route start and end coordinates shift to new hotel address; recalibrates morning transit. |
| **Interests/Vibe** | Itinerary Routing, Weather/Wardrobe | Reselects POIs and adjusts packing recommendations. |
