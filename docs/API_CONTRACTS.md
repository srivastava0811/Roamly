# API Contracts & Client Generation Policy

> **Authoritative Specification**: FastAPI OpenAPI (`apps/api/openapi.json`)
> **Target Consumer Libraries**: `@roamly/api-client` (TypeScript)
> **API Version**: `v1`

---

## 1. OpenAPI Source-of-Truth Policy

The FastAPI backend is the sole authoritative definition of all public API endpoints, models, parameters, and response structures.

1. **Schema Authority**:
   - Pydantic v2 schemas in `apps/api/app/schemas/` define valid request and response shapes.
   - Any modification to data fields, required constraints, query parameters, or status codes must originate in `apps/api/app/schemas/`.
2. **Strict Ban on Manual Client Types**:
   - Neither `apps/web` nor `apps/mobile` may declare independent ad-hoc interfaces representing API responses.
   - All client applications must import models directly from `@roamly/shared-types` or methods from `@roamly/api-client`.
3. **Automated Drift Detection**:
   - In CI, the workflow executes `python scripts/export_openapi.py` to ensure the checked-in `packages/api-client/openapi.json` matches the running application schema.

---

## 2. API Versioning & URL Structure

- Base URL: `https://api.roamly.com` (Production) or `http://localhost:8000` (Local Dev)
- Versioning Scheme: URI Path Prefix (`/api/v1/`)
- Root Non-Versioned Endpoints:
  - `GET /health`: Operational health check. Returns service status for API and Database. Must never require a configured production database.
  - `GET /docs`: Interactive Swagger UI (disabled in strict production).
  - `GET /redoc`: Interactive ReDoc documentation.
  - `GET /openapi.json`: Raw OpenAPI 3.1 specification.

---

## 3. Standard Response & Error Conventions

### 3.1 Success Envelope
All successful resource responses return a standardized envelope:

```typescript
export interface ApiResponseEnvelope<T> {
  data: T;
  meta: {
    requestId?: string;
    timestamp: string; // ISO 8601
    version: string;   // e.g. "0.1.0"
  };
}
```

### 3.2 Error Envelope
When an error occurs, whether 400, 401, 404, 422, or 500, the API returns a structured error object:

```typescript
export interface ApiErrorEnvelope {
  error: {
    code: string;       // e.g. "VALIDATION_ERROR", "NOT_FOUND", "QUOTA_EXCEEDED"
    message: string;    // Human-readable summary
    details?: Record<string, unknown>;
  };
}
```

Standard Error Codes:
| HTTP Status | Code String | Meaning |
|---|---|---|
| `400 Bad Request` | `BAD_REQUEST` | Malformed JSON or invalid parameter syntax |
| `401 Unauthorized` | `UNAUTHORIZED` | Missing or invalid Supabase JWT |
| `403 Forbidden` | `FORBIDDEN` | Insufficient permissions for trip or group |
| `404 Not Found` | `NOT_FOUND` | Entity with specified ID does not exist |
| `422 Unprocessable`| `VALIDATION_ERROR`| Pydantic validation failure (e.g. end date before start date) |
| `429 Too Many Req` | `QUOTA_EXCEEDED` | Upstream provider or AI token rate limit hit |
| `500 Server Error` | `INTERNAL_ERROR` | Unhandled exception (masked in production) |
| `502 Bad Gateway`  | `PROVIDER_ERROR` | External flight/hotel provider failure with retryable flag |

---

## 4. Client Generation & Reproduction Workflow

The TypeScript API client in `packages/api-client` is generated from the OpenAPI contract.

### Command
```bash
# Using root workspace command:
pnpm run generate:client

# Or directly running the generator script:
node scripts/generate-client.mjs
```

### Mechanism
The script operates in two reproducible modes:
1. **Offline Mode (Default & Preferred)**:
   - Invokes `scripts/export_openapi.py` using Python (`apps/api/.venv`).
   - Instantiates the FastAPI application in memory without opening network ports.
   - Dumps the exact OpenAPI 3.1 JSON tree to `packages/api-client/openapi.json`.
2. **Online Mode (Fallback)**:
   - If Python is not on the local path (e.g. pure frontend environment), it queries `http://localhost:8000/openapi.json`.
   - Saves the response to `packages/api-client/openapi.json`.

After the schema is written, `packages/api-client` compiles its typed wrapper classes (`RoamlyApiClient`, `ApiClientError`, `NetworkError`).
