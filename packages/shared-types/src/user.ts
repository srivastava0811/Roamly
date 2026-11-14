export interface User {
  id: string; // Supabase auth UUID
  email: string;
  fullName?: string;
  avatarUrl?: string;
  preferredCurrency: string;
  locale: string;
  createdAt: string;
  updatedAt: string;
}

export interface Traveler {
  id: string;
  userId?: string; // Optional if non-registered guest traveler in a group trip
  tripId: string;
  name: string;
  email?: string;
  ageCategory: 'adult' | 'teen' | 'child' | 'infant';
  dietaryRestrictions: string[];
  mobilityNeeds?: string[];
  preferencesNotes?: string;
  createdAt: string;
  updatedAt: string;
}
