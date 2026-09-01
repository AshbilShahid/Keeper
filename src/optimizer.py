"""
KEEPER — Optimization Engine (Google OR-Tools)

MAXIMIZE   sum( Benefit(i) * x(i) )
SUBJECT TO sum( Cost(i) * x(i) ) <= Budget
           at most one intervention per zone
           each intervention type used <= its implementation_capacity
           x(i) in {0, 1}

This is a 0/1 knapsack-style integer program: given a fixed budget,
choose the combination of (zone, intervention) pairs that maximizes
total modeled benefit.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd
from ortools.linear_solver import pywraplp


def optimize(
    benefits: pd.DataFrame,
    budget: float,
    objective: str = "maximum_population_benefit",
    objectives_config: Optional[dict] = None,
) -> dict:
    """
    Solve the 0/1 knapsack investment problem.

    `objective` blends population benefit vs. raw risk-reduction points
    per the weights in config/objectives.json. Defaults to pure
    population benefit if no config is supplied.
    """
    solver = pywraplp.Solver.CreateSolver("CBC")
    if solver is None:
        raise RuntimeError("Could not create OR-Tools CBC solver.")

    df = benefits.reset_index(drop=True)
    n = len(df)

    # Resolve objective weighting (population benefit vs risk reduction)
    pop_w, risk_w = 1.0, 0.0
    if objectives_config:
        for o in objectives_config.get("objectives", []):
            if o["id"] == objective:
                pop_w, risk_w = o["population_weight"], o["risk_weight"]
                break

    # normalize risk points onto a comparable 0-100-ish scale using max in set
    max_risk_pts = df["expected_risk_points_reduced"].max() or 1
    df["_blended_score"] = (
        pop_w * df["benefit_score"]
        + risk_w * (df["expected_risk_points_reduced"] / max_risk_pts * df["benefit_score"].max())
    )

    x = [solver.BoolVar(f"x_{i}") for i in range(n)]

    # Budget constraint
    solver.Add(solver.Sum(df.loc[i, "cost"] * x[i] for i in range(n)) <= budget)

    # At most one intervention per zone
    for zone_id in df["zone_id"].unique():
        idxs = df.index[df["zone_id"] == zone_id].tolist()
        solver.Add(solver.Sum(x[i] for i in idxs) <= 1)

    # Implementation capacity per intervention type
    for intervention_id in df["intervention_id"].unique():
        idxs = df.index[df["intervention_id"] == intervention_id].tolist()
        capacity = df.loc[idxs[0], "implementation_capacity"]
        solver.Add(solver.Sum(x[i] for i in idxs) <= int(capacity))

    solver.Maximize(solver.Sum(df.loc[i, "_blended_score"] * x[i] for i in range(n)))

    status = solver.Solve()
    if status not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        return {
            "status": "infeasible",
            "total_cost": 0, "remaining_budget": budget,
            "population_benefit": 0, "risk_reduction": 0,
            "recommendations": [],
        }

    selected_idx = [i for i in range(n) if x[i].solution_value() > 0.5]
    selected = df.loc[selected_idx].sort_values("benefit_score", ascending=False)

    total_cost = float(selected["cost"].sum())
    population_benefit = float(selected["expected_population_helped"].sum())

    baseline_total_risk = df.drop_duplicates("zone_id")["flood_risk"].sum()
    risk_points_reduced = float(selected["expected_risk_points_reduced"].sum())
    risk_reduction_pct = round((risk_points_reduced / baseline_total_risk) * 100, 1) if baseline_total_risk else 0.0

    recommendations = [
        {
            "zone_id": row.zone_id,
            "zone_name": row.zone_name,
            "intervention_id": row.intervention_id,
            "intervention_name": row.intervention_name,
            "cost": float(row.cost),
            "benefit_score": float(row.benefit_score),
            "population_helped": float(row.expected_population_helped),
            "risk_class": row.risk_class,
        }
        for row in selected.itertuples()
    ]

    return {
        "status": "optimal" if status == pywraplp.Solver.OPTIMAL else "feasible",
        "budget": budget,
        "total_cost": total_cost,
        "remaining_budget": round(budget - total_cost, 2),
        "population_benefit": population_benefit,
        "risk_reduction": risk_reduction_pct,
        "recommendations": recommendations,
    }
