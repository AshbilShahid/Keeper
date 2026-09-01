# KEEPER — Data

## ⚠️ Demonstration dataset — not official government data

`data/sample/zones.csv` and `data/sample/zones.geojson` contain **30 synthetic
Lahore zones**. Zone names are drawn from real Lahore neighborhoods for
narrative plausibility, but every numeric field
(`population`, `flood_exposure`, `drainage_vulnerability`, `rainfall_risk`,
`infrastructure_vulnerability`) is **randomly generated** and does **not**
represent real measurements, surveys, or official statistics.

This dataset exists to prove the KEEPER pipeline works end-to-end
(risk scoring → benefit scoring → optimization → visualization) before
real data is sourced. Do not cite these numbers as facts about Lahore.

## Fields

| Column | Meaning | Range |
|---|---|---|
| `zone_id` | Unique zone identifier | `Z01`–`Z30` |
| `zone_name` | Illustrative neighborhood name | — |
| `population` | Synthetic resident count | 15,000–65,000 |
| `flood_exposure` | Synthetic exposure index | 0–100 |
| `drainage_vulnerability` | Synthetic drainage index | 0–100 |
| `rainfall_risk` | Synthetic rainfall-risk index | 0–100 |
| `infrastructure_vulnerability` | Synthetic infrastructure index | 0–100 |
| `lat`, `lon` | Approximate point within Lahore's bounding box | — |

## Replacing with real data (Step 11 in the roadmap)

Once the engine and UI work end-to-end on synthetic data, replace this file
with sourced data (e.g. WASA drainage records, PDMA flood hazard maps,
census/population data) using the **same column schema**, so no code in
`src/` needs to change. Clearly label each column's provenance in a revised
version of this file when that happens.
