import { Coordinates, Money, ProvenanceMetadata } from './common';
import { TripStatus } from './enums';

export interface Destination {
  id: string;
  name: string;
  country: string;
  region?: string;
  coordinates: Coordinates;
  timezone: string;
  description?: string;
  heroImageUrl?: string;
}

export interface TripPreference {
  id: string;
  tripId: string;
  pace: 'relaxed' | 'balanced' | 'fast_paced';
  budgetTier: 'ultra_budget' | 'budget' | 'moderate' | 'upscale' | 'luxury';
  interests: string[]; // e.g. ["history", "food", "hiking", "art"]
  avoidCategories: string[];
  dietaryPreferences: string[];
  maxDailyWalkingHours?: number;
  accessibilityNeeds: string[];
  climatePreferences?: string[];
}

export interface Trip {
  id: string;
  title: string;
  description?: string;
  creatorId: string;
  status: TripStatus;
  startDate: string; // ISO 8601 YYYY-MM-DD
  endDate: string; // ISO 8601 YYYY-MM-DD
  destination: Destination;
  origin?: Destination;
  partySize: number;
  totalBudget?: Money;
  currentRevisionId: string;
  createdAt: string;
  updatedAt: string;
}

export interface TripRevision {
  id: string;
  tripId: string;
  revisionNumber: number;
  changeSummary: string;
  triggerSource: 'user_edit' | 'agent_replan' | 'provider_update' | 'group_vote';
  snapshotData: Record<string, unknown>;
  createdAt: string;
  createdBy: string;
}
