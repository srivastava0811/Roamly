'use client';

import { useEffect, useState } from 'react';
import { RoamlyApiClient } from '@roamly/api-client';
import { HealthResponse } from '@roamly/shared-types';
import { Badge } from '@/components/ui/badge';
import { Activity, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';

export function SystemStatus() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const client = new RoamlyApiClient({
        baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      });
      const res = await client.getHealth();
      setHealth(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to connect to API');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <div className="flex items-center gap-2 text-xs text-neutral-600 bg-neutral-50 px-3 py-1.5 rounded-full border border-neutral-200">
      <span className="flex items-center gap-1.5 font-medium">
        <Activity className="w-3.5 h-3.5 text-emerald-600" />
        Backend API:
      </span>
      {loading ? (
        <span className="flex items-center gap-1 text-neutral-400">
          <RefreshCw className="w-3 h-3 animate-spin" />
          Checking...
        </span>
      ) : error ? (
        <span className="flex items-center gap-1 text-amber-600">
          <AlertTriangle className="w-3 h-3" />
          Offline ({error.slice(0, 20)}...)
        </span>
      ) : health ? (
        <span className="flex items-center gap-1 text-emerald-600 font-semibold">
          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
          v{health.version} ({health.environment})
        </span>
      ) : null}
    </div>
  );
}
