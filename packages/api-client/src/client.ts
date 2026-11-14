import {
  HealthResponse,
  Trip,
  AgentEvent,
  ApiResponseEnvelope,
} from '@roamly/shared-types';
import { ApiClientError, NetworkError, UnauthorizedError } from './errors';

export interface ApiClientConfig {
  baseUrl: string;
  getAuthToken?: () => Promise<string | null> | string | null;
  headers?: Record<string, string>;
}

export interface CreateTripRequest {
  title: string;
  description?: string;
  startDate: string;
  endDate: string;
  destinationCity: string;
  destinationCountry: string;
  partySize: number;
  currency?: string;
  totalBudget?: number;
}

export class RoamlyApiClient {
  private baseUrl: string;
  private getAuthToken?: () => Promise<string | null> | string | null;
  private customHeaders: Record<string, string>;

  constructor(config: ApiClientConfig) {
    this.baseUrl = config.baseUrl.replace(/\/+$/, '');
    this.getAuthToken = config.getAuthToken;
    this.customHeaders = config.headers || {};
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...this.customHeaders,
      ...((options.headers as Record<string, string>) || {}),
    };

    if (this.getAuthToken) {
      const token = await this.getAuthToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    let response: Response;
    try {
      response = await fetch(url, {
        ...options,
        headers,
      });
    } catch (err: unknown) {
      throw new NetworkError(err instanceof Error ? err.message : 'Unknown network failure');
    }

    if (!response.ok) {
      let errorBody: unknown;
      try {
        errorBody = await response.json();
      } catch {
        errorBody = await response.text();
      }

      if (response.status === 401) {
        throw new UnauthorizedError('Unauthorized access');
      }

      const message =
        typeof errorBody === 'object' && errorBody !== null && 'detail' in errorBody
          ? String((errorBody as { detail: unknown }).detail)
          : `HTTP Error ${response.status}: ${response.statusText}`;

      throw new ApiClientError(message, response.status, errorBody);
    }

    return (await response.json()) as T;
  }

  /**
   * Health check endpoint
   */
  public async getHealth(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health');
  }

  /**
   * Get all trips accessible to current user
   */
  public async getTrips(): Promise<ApiResponseEnvelope<Trip[]>> {
    return this.request<ApiResponseEnvelope<Trip[]>>('/api/v1/trips');
  }

  /**
   * Get specific trip details by ID
   */
  public async getTripById(id: string): Promise<ApiResponseEnvelope<Trip>> {
    return this.request<ApiResponseEnvelope<Trip>>(`/api/v1/trips/${encodeURIComponent(id)}`);
  }

  /**
   * Create a new draft trip
   */
  public async createTrip(data: CreateTripRequest): Promise<ApiResponseEnvelope<Trip>> {
    return this.request<ApiResponseEnvelope<Trip>>('/api/v1/trips', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Subscribe to Server-Sent Events for agent execution progress
   */
  public streamAgentRun(
    runId: string,
    onEvent: (event: AgentEvent) => void,
    onError?: (error: Error) => void
  ): () => void {
    const url = `${this.baseUrl}/api/v1/agents/runs/${encodeURIComponent(runId)}/stream`;
    
    // In Node or React Native environments where EventSource may require polyfills,
    // this can use fetch reader or standard EventSource in browser.
    if (typeof EventSource !== 'undefined') {
      const eventSource = new EventSource(url);
      eventSource.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data) as AgentEvent;
          onEvent(parsed);
        } catch (err) {
          if (onError) onError(err instanceof Error ? err : new Error('Failed to parse SSE payload'));
        }
      };
      eventSource.onerror = (err) => {
        if (onError) onError(new Error(`EventSource error: ${JSON.stringify(err)}`));
      };
      return () => {
        eventSource.close();
      };
    }

    // Fallback for non-browser environments: return no-op cleanup
    return () => {};
  }
}
