import hashlib
from datetime import datetime, timezone
from typing import List, Dict
from app.schemas.common import MoneySchema
from app.schemas.budget import BudgetBreakdownSchema, CategoryBudgetSchema


class BudgetService:
    @staticmethod
    def to_cents(amount: float) -> int:
        return round(amount * 100)

    @staticmethod
    def from_cents(cents: int) -> float:
        return cents / 100.0

    @classmethod
    def calculate_breakdown(
        cls,
        trip_id: str,
        currency: str,
        total_budget: float,
        category_estimates: Dict[str, float],
        actual_expenses: Dict[str, float] = None,
    ) -> BudgetBreakdownSchema:
        actual_expenses = actual_expenses or {}
        categories = ["transportation", "lodging", "activities", "dining", "contingency"]

        total_budget_cents = cls.to_cents(total_budget)
        total_estimated_cents = 0
        total_actual_cents = 0

        # Standard default budget distribution ratios if categories are not yet planned
        default_distribution = {
            "transportation": 0.30,
            "lodging": 0.35,
            "activities": 0.15,
            "dining": 0.15,
            "contingency": 0.05,
        }

        category_schemas: List[CategoryBudgetSchema] = []

        for cat in categories:
            ratio = default_distribution.get(cat, 0.0)
            allocated_cents = round(total_budget_cents * ratio)
            est_cents = cls.to_cents(category_estimates.get(cat, 0.0))
            act_cents = cls.to_cents(actual_expenses.get(cat, 0.0))

            total_estimated_cents += est_cents
            total_actual_cents += act_cents

            status = "on_track"
            if est_cents > allocated_cents:
                status = "warning"
            if act_cents > allocated_cents:
                status = "exceeded"

            category_schemas.append(
                CategoryBudgetSchema(
                    category=cat,
                    allocated=MoneySchema(amount=cls.from_cents(allocated_cents), currency=currency),
                    estimated_spent=MoneySchema(amount=cls.from_cents(est_cents), currency=currency),
                    actual_spent=MoneySchema(amount=cls.from_cents(act_cents), currency=currency),
                    status=status,
                )
            )

        remaining_cents = total_budget_cents - total_estimated_cents

        # Compute deterministic checksum
        raw_digest = f"{trip_id}:{total_budget_cents}:{total_estimated_cents}:{total_actual_cents}"
        checksum = hashlib.sha256(raw_digest.encode("utf-8")).hexdigest()[:16]

        return BudgetBreakdownSchema(
            id=f"budget-{trip_id}",
            trip_id=trip_id,
            currency=currency,
            total_budget=MoneySchema(amount=cls.from_cents(total_budget_cents), currency=currency),
            total_estimated_cost=MoneySchema(amount=cls.from_cents(total_estimated_cents), currency=currency),
            total_actual_cost=MoneySchema(amount=cls.from_cents(total_actual_cents), currency=currency),
            remaining_estimated_budget=MoneySchema(amount=cls.from_cents(remaining_cents), currency=currency),
            categories=category_schemas,
            deterministic_checksum=checksum,
            last_recalculated_at=datetime.now(timezone.utc),
        )
