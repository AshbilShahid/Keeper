"""
KEEPER — Risk Engine

Calculates a transparent, explainable 0-100 flood risk score per zone,
plus a population-exposure score. Intentionally simple weighted-sum
formulas — no black-box models — so every number can be explained to
a policymaker in one sentence.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import pandas as pd

DEFAULT_WEIGHTS_PATH = Path(__file__).resolve().parent.parent / "config" / "weights.json"


def load_weights(scenario: str = "flood", weights_path: Optional[Path] = None) -> dict:
    """Load the risk-weighting formula for a scenario (e.g. 'flood')."""
    path = weights_path or DEFAULT_WEIGHTS_PATH
    with open(path) as f:
        all_weights = json.load(f)
    if scenario not in all_weights:
        raise KeyError(
            f"No weights configured for scenario '{scenario}'. "
            f"Available: {[k for k in all_weights if not k.startswith('_')]}"
        )
    return all_weights[scenario]


def classify_risk(score: float) -> str:
    """Bucket a 0-100 risk score into a policymaker-friendly label."""
    if score <= 30:
        return "LOW"
    elif score <= 60:
        return "MODERATE"
    elif score <= 80:
        return "HIGH"
    else:
        return "CRITICAL"


def calculate_flood_risk(zones: pd.DataFrame, weights: dict) -> pd.DataFrame:
    """
    Flood Risk = w1*flood_exposure + w2*drainage_vulnerability
               + w3*rainfall_risk + w4*infrastructure_vulnerability

    All inputs are expected on a 0-100 scale, so the weighted sum is
    already 0-100 as long as weights sum to 1.0.
    """
    df = zones.copy()
    df["flood_risk"] = (
        weights["flood_exposure"] * df["flood_exposure"]
        + weights["drainage_vulnerability"] * df["drainage_vulnerability"]
        + weights["rainfall_risk"] * df["rainfall_risk"]
        + weights["infrastructure_vulnerability"] * df["infrastructure_vulnerability"]
    ).round(2)
    df["risk_class"] = df["flood_risk"].apply(classify_risk)
    return df


def calculate_population_exposure(df: pd.DataFrame) -> pd.DataFrame:
    """
    Population Exposure = population * flood_risk, normalized to 0-100
    so it's comparable across zones regardless of population size.

    This answers "which intervention protects the most people?" rather
    than just "which location is most flooded?".
    """
    df = df.copy()
    raw = df["population"] * df["flood_risk"]
    max_raw = raw.max()
    df["population_exposure_raw"] = raw
    df["population_exposure"] = (raw / max_raw * 100).round(2) if max_raw > 0 else 0.0
    return df


def run_risk_engine(zones_csv: str, scenario: str = "flood") -> pd.DataFrame:
    """End-to-end: load zones CSV -> risk score -> population exposure."""
    zones = pd.read_csv(zones_csv)
    weights = load_weights(scenario)
    scored = calculate_flood_risk(zones, weights)
    scored = calculate_population_exposure(scored)
    return scored


if __name__ == "__main__":
    import sys

    csv_path = sys.argv[1] if len(sys.argv) > 1 else "data/sample/zones.csv"
    result = run_risk_engine(csv_path)
    cols = ["zone_id", "zone_name", "population", "flood_risk", "risk_class", "population_exposure"]
    print(result[cols].sort_values("flood_risk", ascending=False).to_string(index=False))
