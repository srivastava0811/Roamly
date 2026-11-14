import { ProvenanceType } from './enums';

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface Address {
  line1?: string;
  line2?: string;
  city?: string;
  stateOrProvince?: string;
  postalCode?: string;
  countryCode?: string;
  formattedAddress: string;
}

export interface Money {
  amount: number; // Stored in minor currency units (cents) or decimal; here standardized as major decimal e.g. 150.00
  currency: string; // ISO 4217, e.g. "USD"
}

export interface ProvenanceMetadata {
  source: ProvenanceType;
  providerName?: string;
  fetchedAt?: string;
  confidenceScore?: number; // 0.0 - 1.0
  notes?: string;
}

export interface ApiResponseEnvelope<T> {
  data: T;
  meta?: {
    requestId: string;
    timestamp: string;
    version: string;
  };
}

export interface ApiErrorDetail {
  code: string;
  message: string;
  field?: string;
}

export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    details?: ApiErrorDetail[];
    requestId?: string;
    timestamp?: string;
  };
}

export interface HealthResponse {
  status: 'ok' | 'degraded' | 'maintenance';
  version: string;
  environment: string;
  timestamp: string;
  services: {
    api: 'ok' | 'degraded' | 'down';
    database: 'ok' | 'degraded' | 'down' | 'unconfigured';
  };
}
