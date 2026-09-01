"""
KEEPER — Scenario Loader

Bundles a city + scenario (e.g. Lahore + flood) + objective into one
config object, so the core engine never hardcodes a city or hazard
type. Adding a new city or scenario means adding a JSON file, not
touching engine code.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


class Scenario:
    def __init__(
        self,
        city_path: Optional[Path] = None,
        interventions_path: Optional[Path] = None,
        objectives_path: Optional[Path] = None,
        weights_path: Optional[Path] = None,
        scenario_name: Optional[str] = None,
    ):
        self.city = load_json(city_path or ROOT / "config" / "city.json")
        self.interventions = load_json(interventions_path or ROOT / "config" / "interventions.json")
        self.objectives = load_json(objectives_path or ROOT / "config" / "objectives.json")
        self.weights = load_json(weights_path or ROOT / "config" / "weights.json")
        self.scenario_name = scenario_name or self.city.get("default_scenario", "flood")

    @property
    def zones_file(self) -> str:
        return str(ROOT / self.city["zones_file"])

    @property
    def default_budget(self) -> float:
        return self.city.get("default_budget", 100_000_000)

    def objective_choices(self) -> list[str]:
        return [o["id"] for o in self.objectives["objectives"]]
