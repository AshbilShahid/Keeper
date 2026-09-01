import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from risk_engine import calculate_flood_risk, calculate_population_exposure, classify_risk  # noqa: E402


WEIGHTS = {
    "flood_exposure": 0.35,
    "drainage_vulnerability": 0.30,
    "rainfall_risk": 0.20,
    "infrastructure_vulnerability": 0.15,
}


def test_classify_risk_buckets():
    assert classify_risk(0) == "LOW"
    assert classify_risk(30) == "LOW"
    assert classify_risk(31) == "MODERATE"
    assert classify_risk(60) == "MODERATE"
    assert classify_risk(61) == "HIGH"
    assert classify_risk(80) == "HIGH"
    assert classify_risk(81) == "CRITICAL"
    assert classify_risk(100) == "CRITICAL"


def test_flood_risk_is_weighted_sum_within_0_100():
    zones = pd.DataFrame([
        {"zone_id": "Z01", "flood_exposure": 100, "drainage_vulnerability": 100,
         "rainfall_risk": 100, "infrastructure_vulnerability": 100},
        {"zone_id": "Z02", "flood_exposure": 0, "drainage_vulnerability": 0,
         "rainfall_risk": 0, "infrastructure_vulnerability": 0},
    ])
    scored = calculate_flood_risk(zones, WEIGHTS)
    assert scored.loc[0, "flood_risk"] == pytest.approx(100.0)
    assert scored.loc[1, "flood_risk"] == pytest.approx(0.0)
    assert scored.loc[0, "risk_class"] == "CRITICAL"
    assert scored.loc[1, "risk_class"] == "LOW"


def test_population_exposure_scales_with_population_and_risk():
    zones = pd.DataFrame([
        {"zone_id": "Z01", "population": 1000, "flood_exposure": 100, "drainage_vulnerability": 100,
         "rainfall_risk": 100, "infrastructure_vulnerability": 100},
        {"zone_id": "Z02", "population": 1000, "flood_exposure": 10, "drainage_vulnerability": 10,
         "rainfall_risk": 10, "infrastructure_vulnerability": 10},
    ])
    scored = calculate_flood_risk(zones, WEIGHTS)
    exposed = calculate_population_exposure(scored)
    # higher risk zone with equal population should have higher exposure
    assert exposed.loc[0, "population_exposure"] > exposed.loc[1, "population_exposure"]
    # the max exposure zone should normalize to 100
    assert exposed["population_exposure"].max() == 100.0
