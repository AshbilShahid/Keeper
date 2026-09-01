import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from optimizer import optimize  # noqa: E402


def make_benefits():
    return pd.DataFrame([
        {"zone_id": "Z01", "zone_name": "Zone A", "flood_risk": 90, "risk_class": "CRITICAL",
         "intervention_id": "drainage_upgrade", "intervention_name": "Drainage Upgrade",
         "cost": 10_000_000, "implementation_capacity": 5,
         "benefit_score": 90.0, "expected_risk_points_reduced": 22.5, "expected_population_helped": 8000},
        {"zone_id": "Z02", "zone_name": "Zone B", "flood_risk": 40, "risk_class": "MODERATE",
         "intervention_id": "drain_maintenance", "intervention_name": "Drain Maintenance",
         "cost": 3_000_000, "implementation_capacity": 10,
         "benefit_score": 20.0, "expected_risk_points_reduced": 4.0, "expected_population_helped": 3000},
        {"zone_id": "Z03", "zone_name": "Zone C", "flood_risk": 70, "risk_class": "HIGH",
         "intervention_id": "green_infrastructure", "intervention_name": "Green Infrastructure",
         "cost": 8_000_000, "implementation_capacity": 6,
         "benefit_score": 50.0, "expected_risk_points_reduced": 12.6, "expected_population_helped": 5000},
    ])


def test_optimizer_respects_budget_constraint():
    benefits = make_benefits()
    result = optimize(benefits, budget=10_000_000)
    assert result["total_cost"] <= 10_000_000
    assert result["status"] in ("optimal", "feasible")


def test_optimizer_picks_higher_benefit_when_affordable():
    benefits = make_benefits()
    # budget only fits exactly one of the three
    result = optimize(benefits, budget=10_000_000)
    chosen_ids = {r["zone_id"] for r in result["recommendations"]}
    # Zone A has the best benefit score (90) and fits the budget (10M)
    assert "Z01" in chosen_ids


def test_optimizer_zero_budget_returns_no_recommendations():
    benefits = make_benefits()
    result = optimize(benefits, budget=0)
    assert result["recommendations"] == []
    assert result["total_cost"] == 0


def test_optimizer_larger_budget_allows_more_investments():
    benefits = make_benefits()
    small = optimize(benefits, budget=10_000_000)
    large = optimize(benefits, budget=25_000_000)
    assert len(large["recommendations"]) >= len(small["recommendations"])
