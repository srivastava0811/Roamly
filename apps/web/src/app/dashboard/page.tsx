'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { formatMoney, calculateDaysBetween } from '@roamly/shared-utils';
import { Trip } from '@roamly/shared-types';
import { Plus, Calendar, MapPin, Users, ArrowUpRight, CheckCircle } from 'lucide-react';

export default function DashboardPage() {
  const [trips] = useState<Trip[]>([
    {
      id: 'trip-preview-1',
      title: 'Alpine Autumn Retreat',
      description: 'Scenic hiking and fondue exploration in the Swiss Alps.',
      creatorId: 'user-default-1',
      status: 'planning',
      startDate: '2026-10-10',
      endDate: '2026-10-18',
      destination: {
        id: 'dest-1',
        name: 'Interlaken',
        country: 'Switzerland',
        coordinates: { latitude: 46.6863, longitude: 7.8632 },
        timezone: 'Europe/Zurich',
      },
      partySize: 2,
      totalBudget: { amount: 2800.0, currency: 'USD' },
      currentRevisionId: 'rev-1',
      createdAt: '2026-11-01T12:00:00Z',
      updatedAt: '2026-11-10T14:30:00Z',
    },
  ]);

  return (
    <div className="container mx-auto px-4 sm:px-6 py-8 sm:py-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-neutral-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-neutral-900 tracking-tight">
            Trip Planning Dashboard
          </h1>
          <p className="mt-1 text-sm text-neutral-500">
            Manage your autonomous travel plans, budgets, and group invitations.
          </p>
        </div>
        <Button className="gap-2">
          <Plus className="w-4 h-4" />
          Create New Trip
        </Button>
      </div>

      {/* Stats Quick View */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs uppercase font-semibold">Active Trips</CardDescription>
            <CardTitle className="text-2xl font-bold text-emerald-600">1</CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-neutral-500">
            1 in collaborative planning stage
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs uppercase font-semibold">Allocated Budget</CardDescription>
            <CardTitle className="text-2xl font-bold text-neutral-900">
              {formatMoney({ amount: 2800, currency: 'USD' })}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-neutral-500">
            Validated by deterministic arithmetic engine
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs uppercase font-semibold">Agent Status</CardDescription>
            <CardTitle className="text-2xl font-bold text-blue-600 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-blue-500" />
              Ready
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-neutral-500">
            8 specialized agent roles registered
          </CardContent>
        </Card>
      </div>

      {/* Trip List */}
      <div className="mt-10">
        <h2 className="text-lg font-semibold text-neutral-900 mb-4">Your Itineraries</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {trips.map((trip) => {
            const days = calculateDaysBetween(trip.startDate, trip.endDate);
            return (
              <Card key={trip.id} className="hover:border-neutral-300 transition-colors">
                <CardHeader>
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <Badge variant="outline" className="mb-2 text-xs">
                        {trip.status.toUpperCase()}
                      </Badge>
                      <CardTitle className="text-xl">{trip.title}</CardTitle>
                      <CardDescription className="mt-1 flex items-center gap-1.5 text-xs">
                        <MapPin className="w-3.5 h-3.5 text-emerald-600" />
                        {trip.destination.name}, {trip.destination.country}
                      </CardDescription>
                    </div>
                    {trip.totalBudget && (
                      <span className="font-semibold text-sm bg-neutral-100 text-neutral-800 px-2.5 py-1 rounded">
                        {formatMoney(trip.totalBudget)}
                      </span>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm text-neutral-600">{trip.description}</p>
                  <div className="flex items-center gap-4 text-xs text-neutral-500 pt-2 border-t border-neutral-100">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5" />
                      {days} Days ({trip.startDate} to {trip.endDate})
                    </span>
                    <span className="flex items-center gap-1">
                      <Users className="w-3.5 h-3.5" />
                      Party of {trip.partySize}
                    </span>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
