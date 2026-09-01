# KEEPER — Assumptions & Limitations

## Data

- The current `data/sample/zones.csv` is a **synthetic demonstration dataset**, not official
  government or survey data. Zone names are real Lahore neighborhoods; the numeric fields
  (population, exposure, vulnerability indices) are randomly generated. See `data/README.md`.
- Coordinates are randomly placed within Lahore's approximate bounding box, not surveyed zone
  boundaries.

## Intervention assumptions

- Costs, risk-reduction percentages, effectiveness figures, and implementation-capacity limits in
  `config/interventions.json` are **illustrative planning assumptions**, chosen to make the
  optimization behave realistically for a demo — they are not sourced from engineering studies.

## Model assumptions

- Risk is a linear weighted sum of four indices. Real flood risk is nonlinear and interacts with
  factors (soil type, upstream development, climate trends) this model doesn't capture.
- The optimizer assumes interventions are independent and their benefits don't overlap or
  interact between neighboring zones.
- Each zone can receive at most one intervention in this version; a real program might combine
  interventions within a zone.

## What this means

**These results are decision-support estimates, not engineering recommendations.** KEEPER is
designed to help a decision-maker reason about trade-offs under a budget constraint — not to
replace hydrological modeling, structural engineering review, or community consultation.

Before any real capital allocation:

1. Replace synthetic zone data with sourced hazard, drainage, and population data.
2. Validate intervention cost/effectiveness assumptions with engineering and planning partners.
3. Re-run the optimization and compare against the demonstration results.
4. Have results reviewed by qualified engineers and local stakeholders.
