"""
KEEPER - Policy Brief Generator

Turns an optimizer result dict into a short, government-style PDF:
Executive Summary, Priority Areas, Recommended Interventions, Budget
Allocation, Expected Benefits, Methodology, Data Sources, Assumptions
& Limitations, Recommended Next Steps.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from fpdf import FPDF


class PolicyBrief(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "KEEPER", ln=True)
        self.set_font("Helvetica", "", 11)
        self.cell(0, 7, "Urban Investment & Resilience Intelligence", ln=True)
        self.set_draw_color(180, 180, 180)
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()} | Decision-support estimate, not an engineering recommendation.", align="C")

    def section(self, title: str, body: str):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(20, 20, 20)
        self.cell(0, 8, title, ln=True)
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5.5, body)
        self.ln(3)


def generate_policy_brief(
    result: dict,
    city_name: str = "Lahore",
    scenario_name: str = "Flood Resilience",
    output_path: str = "demo/policy_brief/KEEPER_Policy_Brief.pdf",
) -> str:
    pdf = PolicyBrief()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, f"{city_name.upper()} {scenario_name.upper()} INVESTMENT BRIEF", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Generated {date.today().isoformat()}", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    rec_lines = "\n".join(
        f"{i+1}. {r['zone_name']} ({r['zone_id']}) - {r['intervention_name']} - "
        f"PKR {r['cost']:,.0f} - benefit score {r['benefit_score']:.1f}"
        for i, r in enumerate(result.get("recommendations", []))
    ) or "No feasible investments within budget."

    pdf.section(
        "Executive Summary",
        f"Given a budget of PKR {result.get('budget', 0):,.0f}, KEEPER identifies the combination of "
        f"zone-level interventions that maximizes modeled public benefit. The recommended portfolio "
        f"commits PKR {result.get('total_cost', 0):,.0f} ({result.get('remaining_budget', 0):,.0f} remaining), "
        f"reaching an estimated {result.get('population_benefit', 0):,.0f} people and reducing modeled "
        f"flood risk by approximately {result.get('risk_reduction', 0)}% across the portfolio's zones.",
    )

    pdf.section("Priority Areas", "\n".join(
        f"- {r['zone_name']} ({r['zone_id']}) - risk class: {r['risk_class']}"
        for r in result.get("recommendations", [])
    ) or "None.")

    pdf.section("Recommended Interventions", rec_lines)

    pdf.section(
        "Budget Allocation",
        f"Total budget: PKR {result.get('budget', 0):,.0f}\n"
        f"Allocated: PKR {result.get('total_cost', 0):,.0f}\n"
        f"Remaining: PKR {result.get('remaining_budget', 0):,.0f}",
    )

    pdf.section(
        "Expected Benefits",
        f"Estimated population benefit: {result.get('population_benefit', 0):,.0f} residents\n"
        f"Estimated risk reduction: {result.get('risk_reduction', 0)}%",
    )

    pdf.section(
        "Methodology",
        "Zone flood risk is a transparent weighted sum of flood exposure, drainage vulnerability, "
        "rainfall risk, and infrastructure vulnerability (0-100 scale). Population exposure combines "
        "risk with population count. For each zone-intervention pair, a benefit score is computed as "
        "population exposure x intervention effectiveness x risk reduction. Google OR-Tools solves a "
        "0/1 knapsack integer program to select the combination of interventions that maximizes total "
        "benefit within the available budget, subject to one intervention per zone and per-intervention "
        "implementation-capacity limits.",
    )

    pdf.section(
        "Data Sources",
        "This brief was generated using a demonstration dataset for Lahore. See data/README.md in the "
        "KEEPER repository for a full description of what is synthetic versus sourced.",
    )

    pdf.section(
        "Assumptions & Limitations",
        "Intervention costs, risk-reduction percentages, and effectiveness figures are illustrative "
        "planning assumptions, not sourced engineering estimates. Zone-level risk and population figures "
        "in the current dataset are synthetic. These results are decision-support estimates, not "
        "engineering recommendations, and should be validated against sourced data and professional "
        "review before informing real capital allocation.",
    )

    pdf.section(
        "Recommended Next Steps",
        "1. Replace synthetic zone data with sourced hazard, drainage, and population data.\n"
        "2. Validate intervention cost and effectiveness assumptions with engineering/planning partners.\n"
        "3. Re-run optimization against validated data and compare results.\n"
        "4. Pilot the top-ranked intervention in the highest-priority zone.",
    )

    pdf.output(output_path)
    return output_path
