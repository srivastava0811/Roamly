from typing import List
from datetime import datetime
from pydantic import BaseModel
from app.schemas.common import MoneySchema


class CategoryBudgetSchema(BaseModel):
    category: str
    allocated: MoneySchema
    estimated_spent: MoneySchema
    actual_spent: MoneySchema
    status: str


class BudgetBreakdownSchema(BaseModel):
    id: str
    trip_id: str
    currency: str
    total_budget: MoneySchema
    total_estimated_cost: MoneySchema
    total_actual_cost: MoneySchema
    remaining_estimated_budget: MoneySchema
    categories: List[CategoryBudgetSchema]
    deterministic_checksum: str
    last_recalculated_at: datetime
