import { AgentRole, AgentRunStatus } from './enums';

export interface AgentEvent {
  id: string;
  runId: string;
  agentRole: AgentRole;
  stepNumber: number;
  stageName: string;
  status: 'started' | 'in_progress' | 'completed' | 'failed' | 'paused';
  message: string;
  metadata?: Record<string, unknown>;
  timestamp: string;
}

export interface AgentRun {
  id: string;
  tripId: string;
  orchestratorRunId?: string;
  agentRole: AgentRole;
  status: AgentRunStatus;
  inputPayload: Record<string, unknown>;
  outputPayload?: Record<string, unknown>;
  error?: string;
  executionDurationMs?: number;
  modelIdentifier?: string;
  startedAt: string;
  completedAt?: string;
}

export interface ReplanningDependency {
  changedField: 'dates' | 'destination' | 'party_size' | 'budget' | 'accommodation' | 'transportation';
  impactedAgents: AgentRole[];
  invalidatedStepIds: string[];
  replanStrategy: 'full' | 'partial_downstream' | 'budget_rebalance_only';
}
