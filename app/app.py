"""
KEEPER — Gradio Application (v2, enhanced UI)

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
import plotly.graph_objects as go  # noqa: E402

from benefit_engine import run_benefit_engine  # noqa: E402
from optimizer import optimize  # noqa: E402
from policy import generate_policy_brief  # noqa: E402
from risk_engine import run_risk_engine  # noqa: E402
from scenario import Scenario  # noqa: E402

SCENARIO = Scenario()

# ---------------------------------------------------------------------------
# Brand palette — urban resilience theme (deep teal / amber alert accents)
# ---------------------------------------------------------------------------
COLOR_INK = "#0F172A"       # near-black slate for headings
COLOR_TEAL = "#0E7C7B"      # primary brand color
COLOR_TEAL_DARK = "#0A5A59"
COLOR_AMBER = "#F59E0B"     # accent / CTA
COLOR_BG_CARD = "#F8FAFC"
COLOR_BORDER = "#E2E8F0"

RISK_COLORS = {
    "LOW": "#22C55E",
    "MODERATE": "#F59E0B",
    "HIGH": "#EF4444",
    "CRITICAL": "#7F1D1D",
}

OBJECTIVE_MAP = {
    "Protect maximum population": "maximum_population_benefit",
    "Reduce maximum risk": "maximum_risk_reduction",
    "Balanced investment": "balanced",
}

CUSTOM_CSS = f"""
.keeper-hero {{
    background: linear-gradient(135deg, {COLOR_TEAL_DARK} 0%, {COLOR_TEAL} 100%);
    border-radius: 16px;
    padding: 28px 32px;
    color: white;
    margin-bottom: 18px;
}}
.keeper-hero h1 {{
    margin: 0 0 4px 0;
    font-size: 28px;
    font-weight: 800;
    letter-spacing: 0.5px;
}}
.keeper-hero p {{
    margin: 0;
    opacity: 0.9;
    font-size: 15px;
}}
.kpi-row {{
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
    margin-bottom: 8px;
}}
.kpi-card {{
    flex: 1;
    min-width: 150px;
    background: {COLOR_BG_CARD};
    border: 1px solid {COLOR_BORDER};
    border-radius: 12px;
    padding: 14px 16px;
}}
.kpi-label {{
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #64748B;
    font-weight: 600;
}}
.kpi-value {{
    font-size: 24px;
    font-weight: 800;
    color: {COLOR_INK};
    margin-top: 2px;
}}
.kpi-value.accent {{ color: {COLOR_TEAL}; }}
.keeper-note {{
    font-size: 12.5px;
    color: #64748B;
    border-left: 3px solid {COLOR_AMBER};
    padding: 8px 12px;
    background: #FFFBEB;
    border-radius: 6px;
    margin-top: 10px;
}}
.zone-pill {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    color: white;
}}
"""

KEEPER_THEME = gr.themes.Soft(
    primary_hue=gr.themes.colors.teal,
    secondary_hue=gr.themes.colors.amber,
    neutral_hue=gr.themes.colors.slate,
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui"],
).set(
    button_primary_background_fill=COLOR_TEAL,
    button_primary_background_fill_hover=COLOR_TEAL_DARK,
    block_title_text_weight="700",
)


def _kpi_html(budget, total_cost, remaining, population_benefit, risk_reduction) -> str:
    def card(label, value, accent=False):
        cls = "kpi-value accent" if accent else "kpi-value"
        return f"""<div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="{cls}">{value}</div>
        </div>"""

    return f"""<div class="kpi-row">
        {card("Budget", f"PKR {budget/1e6:.1f}M")}
        {card("Allocated", f"PKR {total_cost/1e6:.1f}M", accent=True)}
        {card("Remaining", f"PKR {remaining/1e6:.1f}M")}
        {card("Population Benefit", f"{population_benefit:,.0f}", accent=True)}
        {card("Risk Reduction", f"{risk_reduction}%")}
    </div>"""


def _benefit_chart(result: dict) -> go.Figure:
    recs = result.get("recommendations", [])
    if not recs:
        fig = go.Figure()
        fig.update_layout(
            annotations=[dict(text="No investments fit this budget", showarrow=False, font=dict(size=14))],
            height=320, margin=dict(t=20, b=20, l=20, r=20),
        )
        return fig

    df = pd.DataFrame(recs).sort_values("benefit_score", ascending=True)
    labels = [f"{r.zone_name} — {r.intervention_name}" for r in df.itertuples()]
    colors = [RISK_COLORS.get(r.risk_class, "#94A3B8") for r in df.itertuples()]

    fig = go.Figure(go.Bar(
        x=df["benefit_score"], y=labels, orientation="h",
        marker_color=colors,
        text=[f"PKR {c/1e6:.1f}M" for c in df["cost"]],
        textposition="outside",
        hovertemplate="%{y}<br>Benefit score: %{x:.1f}<extra></extra>",
    ))
    fig.update_layout(
        title="Selected Investments — Benefit Score",
        xaxis_title="Benefit Score",
        height=max(320, 34 * len(labels)),
        margin=dict(t=40, b=20, l=20, r=60),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, sans-serif", size=12, color=COLOR_INK),
    )
    return fig


def _build_map(scored: pd.DataFrame, selected_zone_ids: set[str]) -> str:
    center = SCENARIO.city["center"]
    m = folium.Map(
        location=[center["lat"], center["lon"]], zoom_start=SCENARIO.city["default_zoom"],
        tiles="CartoDB positron",
    )

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
            radius=11 if is_selected else 6,
            color="#0F172A" if is_selected else color,
            weight=3 if is_selected else 1,
            fill=True,
            fill_color=color,
            fill_opacity=0.9 if is_selected else 0.7,
            popup=folium.Popup(popup, max_width=250),
        ).add_to(m)

    legend_html = """
    <div style="position: fixed; bottom: 24px; left: 24px; z-index: 9999;
                background: white; padding: 10px 14px; border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.15); font-family: Inter, sans-serif; font-size: 12px;">
      <b>Risk level</b><br>
      <span style="color:#22C55E;">●</span> Low &nbsp;
      <span style="color:#F59E0B;">●</span> Moderate &nbsp;
      <span style="color:#EF4444;">●</span> High &nbsp;
      <span style="color:#7F1D1D;">●</span> Critical
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    return m._repr_html_()


def run_keeper(budget: float, objective_label: str):
    objective_id = OBJECTIVE_MAP[objective_label]

    scored = run_risk_engine(SCENARIO.zones_file, SCENARIO.scenario_name)
    benefits = run_benefit_engine(scored)
    result = optimize(benefits, budget, objective=objective_id, objectives_config=SCENARIO.objectives)

    kpi_html = _kpi_html(
        budget, result["total_cost"], result["remaining_budget"],
        result["population_benefit"], result["risk_reduction"],
    )

    if result["recommendations"]:
        rec_df = pd.DataFrame(result["recommendations"])[
            ["zone_name", "zone_id", "intervention_name", "cost", "benefit_score", "population_helped", "risk_class"]
        ].rename(columns={
            "zone_name": "Zone", "zone_id": "ID", "intervention_name": "Intervention",
            "cost": "Cost (PKR)", "benefit_score": "Benefit Score",
            "population_helped": "Population Helped", "risk_class": "Risk Class",
        })
    else:
        rec_df = pd.DataFrame(columns=["Zone", "ID", "Intervention", "Cost (PKR)", "Benefit Score", "Population Helped", "Risk Class"])

    selected_ids = {r["zone_id"] for r in result["recommendations"]}
    map_html = _build_map(scored, selected_ids)
    chart = _benefit_chart(result)

    explanation = (
        f"**Why this plan?** The selected portfolio prioritizes zones where high population exposure "
        f"overlaps with significant flood vulnerability. The optimizer favors interventions that provide "
        f"the greatest modeled benefit within the available PKR {budget:,.0f} budget, "
        f"objective: *{objective_label}*.\n\n"
        f"<div class='keeper-note'>These results are decision-support estimates, not engineering "
        f"recommendations.</div>"
    )

    return kpi_html, rec_df, map_html, chart, explanation, result


def generate_brief(state_result):
    if not state_result or not state_result.get("recommendations"):
        gr.Warning("No investments to include — try a larger budget.")
        return None
    path = generate_policy_brief(state_result, city_name=SCENARIO.city["city_name"])
    gr.Info("Policy brief generated.")
    return path


def build_app() -> gr.Blocks:
    with gr.Blocks(title="KEEPER — Urban Investment Planner", theme=KEEPER_THEME, css=CUSTOM_CSS) as demo:
        gr.HTML(
            """
            <div class="keeper-hero">
                <h1>🛡️ KEEPER</h1>
                <p>Urban Investment &amp; Resilience Intelligence &nbsp;·&nbsp; Flood resilience demo — Lahore</p>
            </div>
            """
        )

        with gr.Tabs():
            with gr.TabItem("🎛️ Plan & Optimize"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("#### Plan an Investment")
                        budget_slider = gr.Slider(
                            minimum=10_000_000, maximum=200_000_000, step=5_000_000,
                            value=SCENARIO.default_budget, label="Budget (PKR)",
                        )
                        objective_radio = gr.Radio(
                            list(OBJECTIVE_MAP.keys()),
                            value="Protect maximum population", label="Objective",
                        )
                        optimize_btn = gr.Button("⚡ OPTIMIZE", variant="primary", size="lg")
                        explain_btn = gr.Button("💬 Why these investments?")
                        brief_btn = gr.Button("📄 Generate Policy Brief")
                        brief_file = gr.File(label="Policy Brief PDF")

                    with gr.Column(scale=2):
                        kpi_html = gr.HTML()
                        rec_table = gr.Dataframe(label="Top Priorities", interactive=False)
                        explanation_md = gr.Markdown()

            with gr.TabItem("📊 Benefit Comparison"):
                chart_plot = gr.Plot(label="Selected Investments — Benefit Score")

            with gr.TabItem("🗺️ Zone Map"):
                map_html = gr.HTML()

        result_state = gr.State()

        def _run(budget, objective_label):
            kpi, table, mp, chart, explanation, result = run_keeper(budget, objective_label)
            return kpi, table, mp, chart, explanation, result

        optimize_btn.click(
            _run, inputs=[budget_slider, objective_radio],
            outputs=[kpi_html, rec_table, map_html, chart_plot, explanation_md, result_state],
        )

        def _explain(budget, objective_label):
            _, _, _, _, explanation, _ = run_keeper(budget, objective_label)
            return explanation

        explain_btn.click(_explain, inputs=[budget_slider, objective_radio], outputs=explanation_md)
        brief_btn.click(generate_brief, inputs=[result_state], outputs=brief_file)

        demo.load(
            _run, inputs=[budget_slider, objective_radio],
            outputs=[kpi_html, rec_table, map_html, chart_plot, explanation_md, result_state],
        )

    return demo


if __name__ == "__main__":
    build_app().launch()
