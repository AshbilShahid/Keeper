#!/usr/bin/env python3
"""
KEEPER — CLI demo (Milestone 1)

    python run_optimizer.py
    python run_optimizer.py --budget 50000000
    python run_optimizer.py --budget 50000000 --objective maximum_risk_reduction

Proves the core pipeline works before any UI is built:
CSV -> Risk Score -> Benefit Score -> Optimization -> Investment Plan
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from risk_engine import run_risk_engine  # noqa: E402
from benefit_engine import run_benefit_engine  # noqa: E402
from optimizer import optimize  # noqa: E402
from scenario import Scenario  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="KEEPER investment optimizer CLI demo")
    parser.add_argument("--budget", type=float, default=None, help="Budget in PKR (default: config/city.json)")
    parser.add_argument("--objective", type=str, default="maximum_population_benefit",
                         choices=["maximum_population_benefit", "maximum_risk_reduction", "balanced"])
    args = parser.parse_args()

    scenario = Scenario()
    budget = args.budget if args.budget is not None else scenario.default_budget

    scored = run_risk_engine(scenario.zones_file, scenario.scenario_name)
    benefits = run_benefit_engine(scored)
    result = optimize(benefits, budget, objective=args.objective, objectives_config=scenario.objectives)

    W = 44
    print("=" * W)
    print("KEEPER")
    print("Urban Investment & Resilience Engine")
    print("=" * W)
    print(f"City: {scenario.city['city_name']}")
    print(f"Scenario: Flood Resilience")
    print(f"Budget: PKR {budget:,.0f}")
    print("-" * W)
    print("RECOMMENDED INVESTMENTS\n")

    for i, r in enumerate(result["recommendations"], start=1):
        print(f"{i}. {r['zone_name']} ({r['zone_id']})")
        print(f"   {r['intervention_name']}")
        print(f"   Cost: PKR {r['cost']/1e6:.1f}M")
        print(f"   Benefit Score: {r['benefit_score']:.1f}\n")

    print("-" * W)
    print(f"TOTAL INVESTMENT\nPKR {result['total_cost']/1e6:.1f}M\n")
    print(f"REMAINING\nPKR {result['remaining_budget']/1e6:.1f}M\n")
    print(f"POPULATION BENEFIT\n{result['population_benefit']:,.0f}\n")
    print(f"RISK REDUCTION\n{result['risk_reduction']}%")
    print("-" * W)


if __name__ == "__main__":
    main()
