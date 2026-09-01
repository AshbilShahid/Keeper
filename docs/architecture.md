# KEEPER — Architecture

```
KEEPER
  |
  +-- CITY DATA
        |
        v
  +-- RISK ENGINE
        |
        v
  +-- BENEFIT ENGINE
        |
        v
  +-- OPTIMIZER (OR-Tools)
        |
        v
  +-- INVESTMENT PLAN
        |
        +----------+----------+
        v          v          v
      MAP      DASHBOARD  AI EXPLAINER
                              |
                              v
                       POLICY BRIEF PDF
```

## Layers

| Layer | Module | Responsibility |
|---|---|---|
| City Data | `data/sample/zones.csv`, `config/city.json` | Zone-level population and hazard inputs for one city |
| Risk Engine | `src/risk_engine.py` | Transparent weighted-sum flood risk score (0-100) + population exposure |
| Benefit Engine | `src/benefit_engine.py` | Per (zone, intervention) cost, risk reduction, population benefit, benefit score |
| Optimizer | `src/optimizer.py` | 0/1 knapsack integer program (Google OR-Tools) maximizing benefit under a budget constraint |
| Scenario | `src/scenario.py` | Bundles city + scenario + objective config so the engine never hardcodes Lahore or flooding |
| Policy | `src/policy.py` | Renders an optimizer result into a policy-brief PDF |
| App | `app/app.py` | Gradio UI: map, planner, results, what-if slider, AI explanation, policy brief download |

## Design principles

1. **Explainable over black-box.** Risk and benefit are simple weighted formulas a policymaker can
   verify by hand — not a neural network.
2. **The engine doesn't decide, it supports.** Outputs are always framed as decision-support estimates.
3. **The LLM never calculates.** The optimizer computes the plan; the LLM only explains a result it's given.
4. **Config over hardcoding.** City, scenario, objective, and weights are all JSON files, so adding a
   new city or hazard type means adding a config file, not touching engine code.
5. **Works without a GPU or a powerful PC.** The whole pipeline runs in Google Colab.

## Data flow

```
CSV -> Risk Score -> Population Exposure -> Benefit Score (per zone x intervention)
     -> OR-Tools optimization (maximize benefit, budget constraint)
     -> Investment Plan -> {Map, Dashboard tables, AI explanation, Policy Brief PDF}
```
