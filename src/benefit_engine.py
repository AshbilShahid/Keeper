"""
KEEPER — Benefit Engine

For every (zone x intervention) pair, computes cost, expected risk
reduction, population benefit, and a single comparable Benefit Score
that the optimizer maximizes subject to budget.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import pandas as pd

DEFAULT_INTERVENTIONS_PATH = Path(__file__).resolve().parent.parent / "config" / "interventions.json"


def load_interventions(path: Optional[Path] = None) -> pd.DataFrame:
    p = path or DEFAULT_INTERVENTIONS_PATH
    with open(p) as f:
        data = json.load(f)
    return pd.DataFrame(data["interventions"])


def calculate_benefits(scored_zones: pd.DataFrame, interventions: pd.DataFrame) -> pd.DataFrame:
    """
    Cross-join every zone with every intervention and compute:

      Benefit = Population Exposure x Intervention Effectiveness x Risk Reduction

    This rewards interventions that are both effective and applied where
    population exposure is highest -- not just where risk is highest.
    """
    zones = scored_zones.copy()
    zones["_key"] = 1
    interventions = interventions.copy()
    interventions["_key"] = 1

    combos = zones.merge(interventions, on="_key", suffixes=("", "_intervention")).drop(columns="_key")

    combos["benefit_score"] = (
        combos["population_exposure"]
        * combos["population_effectiveness"]
        * combos["risk_reduction"]
    ).round(2)

    combos["expected_risk_points_reduced"] = (combos["flood_risk"] * combos["risk_reduction"]).round(2)
    combos["expected_population_helped"] = (combos["population"] * combos["population_effectiveness"]).round(0)

    keep = [
        "zone_id", "zone_name", "population", "flood_risk", "risk_class", "population_exposure",
        "id", "name", "cost", "risk_reduction", "population_effectiveness", "implementation_capacity",
        "benefit_score", "expected_risk_points_reduced", "expected_population_helped",
    ]
    combos = combos.rename(columns={"id": "intervention_id", "name": "intervention_name"})
    keep = [c if c not in ("id", "name") else {"id": "intervention_id", "name": "intervention_name"}[c] for c in keep]
    return combos[keep].sort_values("benefit_score", ascending=False).reset_index(drop=True)


def run_benefit_engine(scored_zones: pd.DataFrame, interventions_path: Optional[Path] = None) -> pd.DataFrame:
    interventions = load_interventions(interventions_path)
    return calculate_benefits(scored_zones, interventions)


if __name__ == "__main__":
    from risk_engine import run_risk_engine

    scored = run_risk_engine("data/sample/zones.csv")
    benefits = run_benefit_engine(scored)
    print(benefits.head(15).to_string(index=False))
