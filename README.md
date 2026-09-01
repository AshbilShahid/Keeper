# KEEPER
## Urban Investment & Resilience Intelligence

> Give us a city problem and a budget.
> KEEPER helps identify where investment can create the greatest modeled public benefit.

[Demo](#running-the-app) · [Colab](notebooks/04_KEEPER_Full_Demo.ipynb) · [Documentation](docs/)

---

## Problem

Cities don't only face a shortage of information — they face a shortage of resources. A city
planner rarely gets to ask "where is the risk highest?" alone; the real question is **"given a
limited budget, where should we invest to protect the most people?"**

## Solution

KEEPER is a decision-support system that answers exactly that. Give it a city, a hazard scenario,
and a budget, and it returns an optimized investment portfolio — which zones, which
interventions, how much they cost, and how many people they help — plus a plain-language
explanation and a policy-brief PDF.

The first version focuses on **urban flood resilience in Lahore**, on a labeled synthetic
demonstration dataset. The architecture is built to extend to heat, air pollution, waste, and
other city challenges, and to other cities, without changing the core engine.

## How it works

1. **Risk Engine** scores each zone's flood risk (0-100) from a transparent, auditable weighted
   formula — no black-box model.
2. **Benefit Engine** scores every (zone, intervention) pair by how much modeled benefit it would
   deliver.
3. **Optimizer** (Google OR-Tools) solves a 0/1 knapsack problem: maximize total benefit subject
   to the budget.
4. **Investment Plan** feeds a map, a dashboard, an AI-generated plain-language explanation, and a
   policy-brief PDF.

See [`docs/architecture.md`](docs/architecture.md) for the full diagram and
[`docs/methodology.md`](docs/methodology.md) for every formula.

## Architecture

```
CITY DATA -> RISK ENGINE -> BENEFIT ENGINE -> OPTIMIZER (OR-Tools) -> INVESTMENT PLAN
                                                                          |
                                                        +-----------------+-----------------+
                                                        v                 v                 v
                                                      MAP           DASHBOARD        AI EXPLAINER
                                                                                          |
                                                                                          v
                                                                                  POLICY BRIEF PDF
```

## Technology

- **Python** — pandas, Google OR-Tools, folium, Gradio, fpdf2
- **Google Colab** — development, testing, and the primary demo environment (no local GPU or
  powerful PC required)
- **Gradio** — the interactive product itself, runnable from Colab with a shareable public URL

## Demo

Two ways to try KEEPER:

**In Colab (recommended, zero setup):** open
[`notebooks/04_KEEPER_Full_Demo.ipynb`](notebooks/04_KEEPER_Full_Demo.ipynb) and run
**Runtime → Run all**. It clones this repo, installs dependencies, runs risk scoring, benefit
scoring, optimization, a what-if budget comparison, generates a map and a policy brief, and
optionally launches the full interactive Gradio app.

**Locally / via CLI:** see [Installation](#installation) below.

## Data

`data/sample/zones.csv` is a **synthetic demonstration dataset** for 30 illustrative Lahore
zones — clearly labeled as such. See [`data/README.md`](data/README.md) for exactly what's real
(zone names) versus synthetic (every numeric value). Real data sourcing is tracked in
[`docs/data_sources.md`](docs/data_sources.md).

## Methodology

Full formulas for risk scoring, population exposure, benefit scoring, and the optimization model
are documented in [`docs/methodology.md`](docs/methodology.md).

## Limitations

KEEPER's outputs are **decision-support estimates, not engineering recommendations**. Intervention
costs and effectiveness figures are illustrative planning assumptions. See
[`docs/assumptions.md`](docs/assumptions.md) for the full list before treating any output as more
than a demonstration.

## Installation

Requires Python 3.11+.

```bash
git clone https://github.com/<your-username>/keeper.git
cd keeper
pip install -r requirements.txt
```

## Running locally

**CLI demo (Milestone 1 — proves the core pipeline works):**

```bash
python run_optimizer.py
python run_optimizer.py --budget 50000000
python run_optimizer.py --budget 50000000 --objective maximum_risk_reduction
```

**Interactive app (Gradio):**

```bash
python app/app.py
```

Then open the local URL Gradio prints (e.g. `http://127.0.0.1:7860`).

**Tests:**

```bash
pytest tests/ -v
```

## Project structure

```
KEEPER/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── .env.example
├── run_optimizer.py          # CLI demo — Milestone 1
│
├── src/
│   ├── risk_engine.py
│   ├── benefit_engine.py
│   ├── optimizer.py          # Google OR-Tools
│   ├── scenario.py
│   └── policy.py             # Policy brief PDF generator
│
├── config/
│   ├── city.json
│   ├── interventions.json
│   ├── objectives.json
│   └── weights.json
│
├── data/
│   ├── sample/
│   │   ├── zones.csv
│   │   └── zones.geojson
│   └── README.md
│
├── notebooks/
│   └── 04_KEEPER_Full_Demo.ipynb
│
├── app/
│   └── app.py                # Gradio interactive product
│
├── tests/
│   ├── test_risk.py
│   ├── test_optimizer.py
│   └── test_data.py
│
├── docs/
│   ├── architecture.md
│   ├── methodology.md
│   ├── assumptions.md
│   └── data_sources.md
│
└── demo/
    ├── screenshots/
    └── policy_brief/
```

## Future roadmap

1. Replace synthetic Lahore data with sourced hazard, drainage, and population data.
2. Validate intervention cost/effectiveness assumptions with engineering partners.
3. Add heat, air-pollution, and waste scenarios (`config/scenarios/`) using the same engine.
4. Add more cities (`config/cities/`) — the core engine doesn't change.
5. Move the engine behind a FastAPI backend and a React + Vite + Leaflet frontend for a
   production web app, once the Colab/Gradio prototype has proven the concept.
6. Make the AI explanation layer configurable across providers via `AI_PROVIDER`.

---

*KEEPER doesn't decide what a city should build. It helps decision-makers understand where
limited resources can matter most.*
