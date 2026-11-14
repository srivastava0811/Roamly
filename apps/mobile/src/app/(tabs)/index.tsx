import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity } from 'react-native';
import { colors } from '@roamly/design-tokens';
import { Trip, HealthResponse } from '@roamly/shared-types';
import { formatMoney, calculateDaysBetween } from '@roamly/shared-utils';
import { RoamlyApiClient } from '@roamly/api-client';

export default function TripsHomeScreen() {
  const [healthStatus, setHealthStatus] = useState<string>('Checking...');
  const [trips] = useState<Trip[]>([
    {
      id: 'mobile-trip-1',
      title: 'Kyoto Cultural Immersion',
      description: 'Historic temples, gardens, and tea ceremonies.',
      creatorId: 'user-default-1',
      status: 'planning',
      startDate: '2026-11-20',
      endDate: '2026-11-28',
      destination: {
        id: 'dest-kyoto',
        name: 'Kyoto',
        country: 'Japan',
        coordinates: { latitude: 35.0116, longitude: 135.7681 },
        timezone: 'Asia/Tokyo',
      },
      partySize: 2,
      totalBudget: { amount: 3200, currency: 'USD' },
      currentRevisionId: 'rev-mobile-1',
      createdAt: '2026-11-10T00:00:00Z',
      updatedAt: '2026-11-12T00:00:00Z',
    },
  ]);

  useEffect(() => {
    const apiUrl = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';
    const client = new RoamlyApiClient({ baseUrl: apiUrl });
    client
      .getHealth()
      .then((h: HealthResponse) => setHealthStatus(`Online v${h.version} (${h.environment})`))
      .catch(() => setHealthStatus('API Offline'));
  }, []);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* System Status Pill */}
      <View style={styles.statusPill}>
        <View style={styles.statusDot} />
        <Text style={styles.statusText}>Backend: {healthStatus}</Text>
      </View>

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Your Adventures</Text>
        <Text style={styles.subtitle}>Autonomous multi-agent planning on mobile</Text>
      </View>

      {/* Trip Cards */}
      {trips.map((trip) => {
        const days = calculateDaysBetween(trip.startDate, trip.endDate);
        return (
          <TouchableOpacity key={trip.id} style={styles.card} activeOpacity={0.85}>
            <View style={styles.cardHeader}>
              <View>
                <Text style={styles.badge}>{trip.status.toUpperCase()}</Text>
                <Text style={styles.tripTitle}>{trip.title}</Text>
                <Text style={styles.destination}>
                  {trip.destination.name}, {trip.destination.country}
                </Text>
              </View>
              {trip.totalBudget && (
                <View style={styles.budgetPill}>
                  <Text style={styles.budgetText}>{formatMoney(trip.totalBudget)}</Text>
                </View>
              )}
            </View>

            <Text style={styles.tripDescription}>{trip.description}</Text>

            <View style={styles.cardFooter}>
              <Text style={styles.footerText}>
                {days} Days ({trip.startDate} - {trip.endDate})
              </Text>
              <Text style={styles.footerText}>Party of {trip.partySize}</Text>
            </View>
          </TouchableOpacity>
        );
      })}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.neutral[50],
  },
  content: {
    padding: 16,
  },
  statusPill: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: colors.neutral[200],
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    marginBottom: 16,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.brand[500],
    marginRight: 8,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '500',
    color: colors.neutral[700],
  },
  header: {
    marginBottom: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: '800',
    color: colors.neutral[900],
    letterSpacing: -0.5,
  },
  subtitle: {
    fontSize: 14,
    color: colors.neutral[500],
    marginTop: 4,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 18,
    borderWidth: 1,
    borderColor: colors.neutral[200],
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
    marginBottom: 16,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 10,
  },
  badge: {
    fontSize: 10,
    fontWeight: '700',
    color: colors.brand[700],
    backgroundColor: colors.brand[50],
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
    alignSelf: 'flex-start',
    marginBottom: 6,
  },
  tripTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.neutral[900],
  },
  destination: {
    fontSize: 13,
    color: colors.brand[600],
    fontWeight: '500',
    marginTop: 2,
  },
  budgetPill: {
    backgroundColor: colors.neutral[100],
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  budgetText: {
    fontSize: 13,
    fontWeight: '700',
    color: colors.neutral[900],
  },
  tripDescription: {
    fontSize: 13,
    color: colors.neutral[600],
    lineHeight: 18,
    marginBottom: 14,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    borderTopWidth: 1,
    borderTopColor: colors.neutral[100],
    paddingTop: 12,
  },
  footerText: {
    fontSize: 11,
    color: colors.neutral[500],
    fontWeight: '500',
  },
});
