import pytest
from app.services.budget_service import BudgetService


def test_deterministic_budget_calculation():
    breakdown = BudgetService.calculate_breakdown(
        trip_id="test-trip-123",
        currency="USD",
        total_budget=1000.00,
        category_estimates={
            "transportation": 300.00,
            "lodging": 350.00,
            "activities": 150.00,
            "dining": 100.00,
            "contingency": 50.00,
        },
        actual_expenses={
            "transportation": 280.00,
            "dining": 110.00,
        },
    )

    assert breakdown.total_budget.amount == 1000.00
    assert breakdown.total_estimated_cost.amount == 950.00
    assert breakdown.remaining_estimated_budget.amount == 50.00
    assert breakdown.deterministic_checksum is not None
    assert len(breakdown.deterministic_checksum) == 16
    assert len(breakdown.categories) == 5

    # Check categories status
    dining_cat = next(c for c in breakdown.categories if c.category == "dining")
    assert dining_cat.estimated_spent.amount == 100.00
    assert dining_cat.actual_spent.amount == 110.00
