# KEEPER — Methodology

## 1. Flood Risk Score (0-100)

```
Flood Risk = 0.35 x Flood Exposure
           + 0.30 x Drainage Vulnerability
           + 0.20 x Rainfall Risk
           + 0.15 x Infrastructure Vulnerability
```

Each input is itself a 0-100 index. Weights are configured per scenario in `config/weights.json` and
must sum to 1.0.

Classification:

| Range | Class |
|---|---|
| 0-30 | LOW |
| 31-60 | MODERATE |
| 61-80 | HIGH |
| 81-100 | CRITICAL |

## 2. Population Exposure

```
Population Exposure = Population x Flood Risk
```

Normalized to 0-100 across the zone set for comparability. This shifts the question from "which
location is most flooded?" to "which intervention protects the most people?".

## 3. Benefit Score

For every (zone, intervention) pair:

```
Benefit Score = Population Exposure x Intervention Effectiveness x Risk Reduction
```

where `Intervention Effectiveness` and `Risk Reduction` come from `config/interventions.json`.

## 4. Optimization

A 0/1 knapsack integer program solved with Google OR-Tools:

```
MAXIMIZE   sum( Benefit(i) * x(i) )
SUBJECT TO sum( Cost(i) * x(i) ) <= Budget
           at most one intervention per zone
           each intervention type used <= its implementation_capacity
           x(i) in {0, 1}
```

Three objective modes (configured in `config/objectives.json`) blend population benefit and raw
risk-reduction points differently:

- **Protect maximum population** — pure population-benefit weighting
- **Reduce maximum risk** — pure risk-reduction weighting
- **Balanced investment** — equal weighting of both

## 5. What KEEPER does not do

- It does not use a black-box model to compute risk or benefit — every number is traceable to a formula.
- It does not let an LLM calculate the plan — the LLM only explains an already-computed result.
- It does not claim its outputs are engineering recommendations. See `docs/assumptions.md`.
