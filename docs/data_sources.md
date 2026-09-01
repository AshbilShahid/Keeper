# KEEPER — Data Sources

## Current version (v0.1 — demonstration)

| Dataset | Source | Status |
|---|---|---|
| Zone population, flood exposure, drainage vulnerability, rainfall risk, infrastructure vulnerability | Synthetically generated for this demo | **Not official data** |
| Zone names | Real Lahore neighborhood names, used illustratively | Real names, synthetic values |
| Zone coordinates | Randomly placed within Lahore's bounding box | **Not surveyed** |
| Intervention costs & effectiveness | Illustrative planning assumptions | **Not sourced** |

## Candidate sources for a future version (Step 11 in the roadmap)

These are suggested starting points for replacing synthetic data — they have not yet been
integrated and should be verified for licensing and currency before use:

- **WASA (Water and Sanitation Agency, Lahore)** — drainage infrastructure records
- **PDMA Punjab (Provincial Disaster Management Authority)** — flood hazard mapping
- **Pakistan Bureau of Statistics** — population census data by area
- **Punjab Urban Unit** — urban planning and infrastructure datasets
- **OpenStreetMap** — zone boundaries and infrastructure geometry

## Labeling convention going forward

Every dataset added to KEEPER should be tagged as one of:

- **Official / sourced data** — traceable to a named public authority or dataset
- **Derived estimates** — computed from sourced data via a documented formula
- **Demonstration assumptions** — illustrative values used only to exercise the pipeline

`data/README.md` should be updated whenever a dataset's tag changes.
