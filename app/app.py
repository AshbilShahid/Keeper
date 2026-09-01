"""
KEEPER — Gradio Application

Runs entirely in Python (Colab-friendly, no separate frontend/backend
needed for the demo). Launch with:

    python app/app.py

or from Colab:

    from app.app import build_app
    build_app().launch(share=True)
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import folium  # noqa: E402
import gradio as gr  # noqa: E402
import pandas as pd  # noqa: E402

from benefit_engine import run_benefit_engine  # noqa: E402
from optimizer import optimize  # noqa: E402
from policy import generate_policy_brief  # noqa: E402
from risk_engine import run_risk_engine  # noqa: E402
from scenario import Scenario  # noqa: E402

SCENARIO = Scenario()

RISK_COLORS = {"LOW": "green", "MODERATE": "orange", "HIGH": "red", "CRITICAL": "darkred"}


def _build_map(scored: pd.DataFrame, selected_zone_ids: set[str]) -> str:
    center = SCENARIO.city["center"]
    m = folium.Map(location=[center["lat"], center["lon"]], zoom_start=SCENARIO.city["default_zoom"])

    for row in scored.itertuples():
        is_selected = row.zone_id in selected_zone_ids
        color = RISK_COLORS.get(row.risk_class, "gray")
        popup = (
            f"<b>{row.zone_name} ({row.zone_id})</b><br>"
            f"Population: {row.population:,}<br>"
            f"Flood Risk: {row.flood_risk}/100 ({row.risk_class})<br>"
            f"{'⭐ Recommended for investment' if is_selected else ''}"
        )
        folium.CircleMarker(
            location=[row.lat, row.lon],
            radius=10 if is_selected else 6,
            color="black" if is_selected else color,
            weight=3 if is_selected else 1,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            popup=popup,
        ).add_to(m)

    return m._repr_html_()


def run_keeper(budget: float, objective_label: str):
    objective_id = {
        "Protect maximum population": "maximum_population_benefit",
        "Reduce maximum risk": "maximum_risk_reduction",
        "Balanced investment": "balanced",
    }[objective_label]

    scored = run_risk_engine(SCENARIO.zones_file, SCENARIO.scenario_name)
    benefits = run_benefit_engine(scored)
    result = optimize(benefits, budget, objective=objective_id, objectives_config=SCENARIO.objectives)

    summary_md = (
        f"### Optimal Investment Plan\n\n"
        f"| Metric | Value |\n|---|---|\n"
        f"| Budget | PKR {budget:,.0f} |\n"
        f"| Recommended | PKR {result['total_cost']:,.0f} |\n"
        f"| Remaining | PKR {result['remaining_budget']:,.0f} |\n"
        f"| Population Benefit | {result['population_benefit']:,.0f} |\n"
        f"| Risk Reduction | {result['risk_reduction']}% |\n"
    )

    if result["recommendations"]:
        rec_df = pd.DataFrame(result["recommendations"])[
            ["zone_name", "zone_id", "intervention_name", "cost", "benefit_score", "population_helped"]
        ].rename(columns={
            "zone_name": "Zone", "zone_id": "ID", "intervention_name": "Intervention",
            "cost": "Cost (PKR)", "benefit_score": "Benefit Score", "population_helped": "Population Helped",
        })
    else:
        rec_df = pd.DataFrame(columns=["Zone", "ID", "Intervention", "Cost (PKR)", "Benefit Score", "Population Helped"])

    selected_ids = {r["zone_id"] for r in result["recommendations"]}
    map_html = _build_map(scored, selected_ids)

    explanation = (
        f"**Why this plan?** The selected portfolio prioritizes zones where high population exposure "
        f"overlaps with significant flood vulnerability. The optimizer favors interventions that provide "
        f"the greatest modeled benefit within the available PKR {budget:,.0f} budget, objective: "
        f"*{objective_label}*.\n\n"
        f"_These results are decision-support estimates, not engineering recommendations._"
    )

    return summary_md, rec_df, map_html, explanation, result


def generate_brief(state_result):
    if not state_result or not state_result.get("recommendations"):
        return None
    path = generate_policy_brief(state_result, city_name=SCENARIO.city["city_name"])
    return path


def build_app() -> gr.Blocks:
    with gr.Blocks(title="KEEPER — Urban Investment Planner") as demo:
        gr.Markdown(
            "# KEEPER\n"
            "### Urban Investment & Resilience Intelligence\n"
            "Give KEEPER a city problem and a budget — it identifies where investment can create the "
            "greatest modeled public benefit. *Current demo: flood resilience in Lahore, on a synthetic "
            "demonstration dataset.*"
        )

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("#### Plan an Investment")
                budget_slider = gr.Slider(
                    minimum=10_000_000, maximum=200_000_000, step=5_000_000,
                    value=SCENARIO.default_budget, label="Budget (PKR)",
                )
                objective_radio = gr.Radio(
                    ["Protect maximum population", "Reduce maximum risk", "Balanced investment"],
                    value="Protect maximum population", label="Objective",
                )
                optimize_btn = gr.Button("OPTIMIZE", variant="primary")
                explain_btn = gr.Button("Why these investments?")
                brief_btn = gr.Button("Generate Policy Brief")
                brief_file = gr.File(label="Policy Brief PDF", visible=True)

            with gr.Column(scale=2):
                summary_md = gr.Markdown()
                rec_table = gr.Dataframe(label="Top Priorities")
                map_html = gr.HTML(label="Zone Map")
                explanation_md = gr.Markdown()

        result_state = gr.State()

        def _run(budget, objective_label):
            summary, table, mp, _, result = run_keeper(budget, objective_label)
            return summary, table, mp, "", result

        optimize_btn.click(
            _run, inputs=[budget_slider, objective_radio],
            outputs=[summary_md, rec_table, map_html, explanation_md, result_state],
        )

        def _explain(budget, objective_label):
            _, _, _, explanation, _ = run_keeper(budget, objective_label)
            return explanation

        explain_btn.click(_explain, inputs=[budget_slider, objective_radio], outputs=explanation_md)
        brief_btn.click(generate_brief, inputs=[result_state], outputs=brief_file)

        demo.load(_run, inputs=[budget_slider, objective_radio],
                   outputs=[summary_md, rec_table, map_html, explanation_md, result_state])

    return demo


if __name__ == "__main__":
    build_app().launch()
