import { Money } from './common';

export interface CategoryBudget {
  category: 'transportation' | 'lodging' | 'activities' | 'dining' | 'contingency' | 'miscellaneous';
  allocated: Money;
  estimatedSpent: Money;
  actualSpent: Money;
  status: 'on_track' | 'warning' | 'exceeded';
}

export interface BudgetBreakdown {
  id: string;
  tripId: string;
  currency: string;
  totalBudget: Money;
  totalEstimatedCost: Money;
  totalActualCost: Money;
  remainingEstimatedBudget: Money;
  categories: CategoryBudget[];
  deterministicChecksum: string; // Hash/digest of components to ensure arithmetic validity
  lastRecalculatedAt: string;
}
