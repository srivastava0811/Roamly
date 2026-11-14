export type TripStatus =
  | 'draft'
  | 'planning'
  | 'proposed'
  | 'confirmed'
  | 'active'
  | 'completed'
  | 'archived';

export type Currency = 'USD' | 'EUR' | 'GBP' | 'CAD' | 'AUD' | 'JPY' | 'INR';

export type TransportMode =
  | 'flight'
  | 'train'
  | 'bus'
  | 'drive'
  | 'subway'
  | 'walk'
  | 'rideshare'
  | 'ferry';

export type ActivityCategory =
  | 'sightseeing'
  | 'culture'
  | 'food_and_drink'
  | 'outdoor_adventure'
  | 'relaxation'
  | 'shopping'
  | 'entertainment'
  | 'transport'
  | 'lodging';

export type AccommodationType =
  | 'hotel'
  | 'hostel'
  | 'apartment'
  | 'resort'
  | 'guesthouse'
  | 'camping';

export type ProvenanceType =
  | 'live_provider'
  | 'cached_provider'
  | 'deterministic_estimate'
  | 'ai_synthesized'
  | 'fixture_mock'
  | 'user_override';

export type AgentRole =
  | 'orchestrator'
  | 'destination_discovery'
  | 'transportation'
  | 'accommodation'
  | 'itinerary_routing'
  | 'budget'
  | 'weather_wardrobe'
  | 'group_coordination';

export type AgentRunStatus =
  | 'pending'
  | 'running'
  | 'waiting_on_input'
  | 'completed'
  | 'failed'
  | 'cancelled';

export type GroupRole = 'owner' | 'organizer' | 'traveler' | 'viewer';

export type VoteValue = 'up' | 'down' | 'abstain';
