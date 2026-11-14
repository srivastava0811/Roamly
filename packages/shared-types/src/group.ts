import { GroupRole, VoteValue } from './enums';

export interface Group {
  id: string;
  tripId: string;
  name: string;
  inviteCode: string;
  createdAt: string;
  updatedAt: string;
}

export interface GroupMembership {
  id: string;
  groupId: string;
  userId: string;
  role: GroupRole;
  joinedAt: string;
}

export interface GroupVote {
  id: string;
  groupId: string;
  targetType: 'destination' | 'activity' | 'accommodation' | 'transportation';
  targetId: string;
  userId: string;
  vote: VoteValue;
  notes?: string;
  votedAt: string;
}
