import { Coordinates, Money, ProvenanceMetadata } from './common';
import { AccommodationType, ActivityCategory, TransportMode } from './enums';

export interface Activity {
  id: string;
  itineraryDayId: string;
  name: string;
  category: ActivityCategory;
  description?: string;
  startTime?: string; // HH:mm
  endTime?: string; // HH:mm
  durationMinutes: number;
  locationName: string;
  coordinates: Coordinates;
  estimatedCost?: Money;
  bookingRequired: boolean;
  bookingUrl?: string;
  orderIndex: number;
  provenance: ProvenanceMetadata;
}

export interface AccommodationOption {
  id: string;
  tripId: string;
  name: string;
  type: AccommodationType;
  checkInDate: string;
  checkOutDate: string;
  address: string;
  coordinates: Coordinates;
  pricePerNight: Money;
  totalPrice: Money;
  selected: boolean;
  rating?: number;
  amenities: string[];
  bookingUrl?: string;
  provenance: ProvenanceMetadata;
}

export interface TransportationOption {
  id: string;
  tripId: string;
  mode: TransportMode;
  departureTime: string; // ISO 8601
  arrivalTime: string; // ISO 8601
  originName: string;
  originCoordinates?: Coordinates;
  destinationName: string;
  destinationCoordinates?: Coordinates;
  carrierOrProvider?: string;
  estimatedCost: Money;
  selected: boolean;
  carbonEmissionKg?: number;
  provenance: ProvenanceMetadata;
}

export interface ItineraryDay {
  id: string;
  tripId: string;
  dayNumber: number; // 1-indexed
  date: string; // YYYY-MM-DD
  themeTitle?: string;
  weatherSummary?: {
    expectedTemperatureCelsius: number;
    weatherCondition: string;
    precipitationProbability: number;
    recommendedClothing: string[];
  };
  activities: Activity[];
  dailyEstimatedCost: Money;
}
