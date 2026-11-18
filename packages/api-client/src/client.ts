import {
  HealthResponse,
  Trip,
  ItineraryDay,
  Activity,
  BudgetBreakdown,
  AgentEvent,
  AgentRun,
  ApiResponseEnvelope,
  Money,
  Coordinates,
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
  start_date: string;
  end_date: string;
  destination_city: string;
  destination_country: string;
  party_size?: number;
  currency?: string;
  total_budget?: number;
}

export interface UpdateTripRequest {
  title?: string;
  description?: string;
  start_date?: string;
  end_date?: string;
  party_size?: number;
  total_budget?: number;
}

export interface CreateItineraryDayRequest {
  day_number: number;
  date: string;
  theme_title?: string;
  weather_summary?: Record<string, unknown>;
}

export interface UpdateItineraryDayRequest {
  theme_title?: string;
  date?: string;
  weather_summary?: Record<string, unknown>;
}

export interface CreateActivityRequest {
  name: string;
  category?: string;
  description?: string;
  start_time?: string;
  end_time?: string;
  duration_minutes?: number;
  location_name: string;
  latitude: number;
  longitude: number;
  estimated_cost?: Money;
  booking_required?: boolean;
  booking_url?: string;
  order_index?: number;
  provenance_metadata?: Record<string, unknown>;
}

export interface UpdateActivityRequest {
  name?: string;
  category?: string;
  description?: string;
  start_time?: string;
  end_time?: string;
  duration_minutes?: number;
  location_name?: string;
  latitude?: number;
  longitude?: number;
  estimated_cost?: Money;
  booking_required?: boolean;
  booking_url?: string;
  order_index?: number;
  provenance_metadata?: Record<string, unknown>;
}

export interface WeatherForecast {
  forecast_date: string;
  temp_max_celsius: number;
  temp_min_celsius: number;
  weather_condition: string;
  precipitation_probability: number;
  uv_index: number;
  clothing_recommendations: string[];
}

export interface WeatherForecastParams {
  latitude: number;
  longitude: number;
  start_date: string;
  end_date: string;
}

export interface TripPlanRequest {
  preferences?: Record<string, unknown>;
  run_id?: string;
}

export interface TripPlanGenerationResponse {
  run_id: string;
  trip_id: string;
  status: string;
  model_identifier?: string;
  itinerary_days: ItineraryDay[];
  budget_breakdown: BudgetBreakdown;
  packing_list: string[];
}

export interface MutationResult {
  success: boolean;
  id: string;
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
        typeof errorBody === 'object' && errorBody !== null && 'error' in errorBody
          ? String((errorBody as { error: { message?: string } }).error?.message || response.statusText)
          : typeof errorBody === 'object' && errorBody !== null && 'detail' in errorBody
          ? String((errorBody as { detail: unknown }).detail)
          : `HTTP Error ${response.status}: ${response.statusText}`;

      throw new ApiClientError(message, response.status, errorBody);
    }

    return (await response.json()) as T;
  }

  // -----------------------------------------------------------
  // Health
  // -----------------------------------------------------------

  public async getHealth(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health');
  }

  // -----------------------------------------------------------
  // Trips
  // -----------------------------------------------------------

  public async getTrips(): Promise<ApiResponseEnvelope<Trip[]>> {
    return this.request<ApiResponseEnvelope<Trip[]>>('/api/v1/trips');
  }

  public async getTripById(id: string): Promise<ApiResponseEnvelope<Trip>> {
    return this.request<ApiResponseEnvelope<Trip>>(`/api/v1/trips/${encodeURIComponent(id)}`);
  }

  public async createTrip(data: CreateTripRequest): Promise<ApiResponseEnvelope<Trip>> {
    return this.request<ApiResponseEnvelope<Trip>>('/api/v1/trips', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  public async updateTrip(id: string, data: UpdateTripRequest): Promise<ApiResponseEnvelope<Trip>> {
    return this.request<ApiResponseEnvelope<Trip>>(`/api/v1/trips/${encodeURIComponent(id)}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  public async deleteTrip(id: string): Promise<ApiResponseEnvelope<MutationResult>> {
    return this.request<ApiResponseEnvelope<MutationResult>>(`/api/v1/trips/${encodeURIComponent(id)}`, {
      method: 'DELETE',
    });
  }

  public async getTripBudget(tripId: string): Promise<ApiResponseEnvelope<BudgetBreakdown>> {
    return this.request<ApiResponseEnvelope<BudgetBreakdown>>(`/api/v1/trips/${encodeURIComponent(tripId)}/budget`);
  }

  // -----------------------------------------------------------
  // Itinerary Days
  // -----------------------------------------------------------

  public async getItineraryDays(tripId: string): Promise<ApiResponseEnvelope<ItineraryDay[]>> {
    return this.request<ApiResponseEnvelope<ItineraryDay[]>>(`/api/v1/trips/${encodeURIComponent(tripId)}/days`);
  }

  public async getItineraryDay(tripId: string, dayId: string): Promise<ApiResponseEnvelope<ItineraryDay>> {
    return this.request<ApiResponseEnvelope<ItineraryDay>>(
      `/api/v1/trips/${encodeURIComponent(tripId)}/days/${encodeURIComponent(dayId)}`
    );
  }

  public async createItineraryDay(
    tripId: string,
    data: CreateItineraryDayRequest
  ): Promise<ApiResponseEnvelope<ItineraryDay>> {
    return this.request<ApiResponseEnvelope<ItineraryDay>>(`/api/v1/trips/${encodeURIComponent(tripId)}/days`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  public async updateItineraryDay(
    tripId: string,
    dayId: string,
    data: UpdateItineraryDayRequest
  ): Promise<ApiResponseEnvelope<ItineraryDay>> {
    return this.request<ApiResponseEnvelope<ItineraryDay>>(
      `/api/v1/trips/${encodeURIComponent(tripId)}/days/${encodeURIComponent(dayId)}`,
      {
        method: 'PATCH',
        body: JSON.stringify(data),
      }
    );
  }

  public async deleteItineraryDay(tripId: string, dayId: string): Promise<ApiResponseEnvelope<MutationResult>> {
    return this.request<ApiResponseEnvelope<MutationResult>>(
      `/api/v1/trips/${encodeURIComponent(tripId)}/days/${encodeURIComponent(dayId)}`,
      {
        method: 'DELETE',
      }
    );
  }

  // -----------------------------------------------------------
  // Activities
  // -----------------------------------------------------------

  public async getActivities(tripId: string, dayId: string): Promise<ApiResponseEnvelope<Activity[]>> {
    return this.request<ApiResponseEnvelope<Activity[]>>(
      `/api/v1/trips/${encodeURIComponent(tripId)}/days/${encodeURIComponent(dayId)}/activities`
    );
  }

  public async getActivity(
    tripId: string,
    dayId: string,
    activityId: string
  ): Promise<ApiResponseEnvelope<Activity>> {
    return this.request<ApiResponseEnvelope<Activity>>(
      `/api/v1/trips/${encodeURIComponent(tripId)}/days/${encodeURIComponent(dayId)}/activities/${encodeURIComponent(
        activityId
      )}`
    );
  }

  public async createActivity(
    tripId: string,
    dayId: string,
    data: CreateActivityRequest
  ): Promise<ApiResponseEnvelope<Activity>> {
    return this.request<ApiResponseEnvelope<Activity>>(
      `/api/v1/trips/${encodeURIComponent(tripId)}/days/${encodeURIComponent(dayId)}/activities`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  }

  public async updateActivity(
    tripId: string,
    dayId: string,
    activityId: string,
    data: UpdateActivityRequest
  ): Promise<ApiResponseEnvelope<Activity>> {
    return this.request<ApiResponseEnvelope<Activity>>(
      `/api/v1/trips/${encodeURIComponent(tripId)}/days/${encodeURIComponent(dayId)}/activities/${encodeURIComponent(
        activityId
      )}`,
      {
        method: 'PATCH',
        body: JSON.stringify(data),
      }
    );
  }

  public async deleteActivity(
    tripId: string,
    dayId: string,
    activityId: string
  ): Promise<ApiResponseEnvelope<MutationResult>> {
    return this.request<ApiResponseEnvelope<MutationResult>>(
      `/api/v1/trips/${encodeURIComponent(tripId)}/days/${encodeURIComponent(dayId)}/activities/${encodeURIComponent(
        activityId
      )}`,
      {
        method: 'DELETE',
      }
    );
  }

  // -----------------------------------------------------------
  // Weather
  // -----------------------------------------------------------

  public async getWeatherForecast(
    params: WeatherForecastParams
  ): Promise<ApiResponseEnvelope<WeatherForecast[]>> {
    const query = new URLSearchParams({
      latitude: params.latitude.toString(),
      longitude: params.longitude.toString(),
      start_date: params.start_date,
      end_date: params.end_date,
    });
    return this.request<ApiResponseEnvelope<WeatherForecast[]>>(`/api/v1/weather/forecast?${query.toString()}`);
  }

  // -----------------------------------------------------------
  // AI Travel Agents & Realtime Streaming
  // -----------------------------------------------------------

  public async generateTripPlan(
    tripId: string,
    data: TripPlanRequest = {}
  ): Promise<ApiResponseEnvelope<TripPlanGenerationResponse>> {
    return this.request<ApiResponseEnvelope<TripPlanGenerationResponse>>(
      `/api/v1/agents/trips/${encodeURIComponent(tripId)}/plan`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  }

  public async getAgentRun(runId: string): Promise<ApiResponseEnvelope<AgentRun>> {
    return this.request<ApiResponseEnvelope<AgentRun>>(`/api/v1/agents/runs/${encodeURIComponent(runId)}`);
  }

  public async getAgentRunEvents(runId: string): Promise<ApiResponseEnvelope<AgentEvent[]>> {
    return this.request<ApiResponseEnvelope<AgentEvent[]>>(
      `/api/v1/agents/runs/${encodeURIComponent(runId)}/events`
    );
  }

  public streamAgentRun(
    runId: string,
    onEvent: (event: AgentEvent) => void,
    onError?: (error: Error) => void
  ): () => void {
    const url = `${this.baseUrl}/api/v1/agents/runs/${encodeURIComponent(runId)}/stream`;
    
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

    return () => {};
  }
}
