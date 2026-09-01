import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


def test_zones_csv_has_expected_columns():
    df = pd.read_csv(ROOT / "data" / "sample" / "zones.csv")
    expected = {
        "zone_id", "zone_name", "population", "flood_exposure",
        "drainage_vulnerability", "rainfall_risk", "infrastructure_vulnerability",
        "lat", "lon",
    }
    assert expected.issubset(set(df.columns))


def test_zones_csv_has_no_nulls():
    df = pd.read_csv(ROOT / "data" / "sample" / "zones.csv")
    assert df.isnull().sum().sum() == 0


def test_zones_scores_within_0_100():
    df = pd.read_csv(ROOT / "data" / "sample" / "zones.csv")
    for col in ["flood_exposure", "drainage_vulnerability", "rainfall_risk", "infrastructure_vulnerability"]:
        assert df[col].between(0, 100).all()


def test_zone_ids_unique():
    df = pd.read_csv(ROOT / "data" / "sample" / "zones.csv")
    assert df["zone_id"].is_unique


def test_weights_sum_to_one():
    import json
    with open(ROOT / "config" / "weights.json") as f:
        weights = json.load(f)
    flood_weights = weights["flood"]
    assert abs(sum(flood_weights.values()) - 1.0) < 1e-6
