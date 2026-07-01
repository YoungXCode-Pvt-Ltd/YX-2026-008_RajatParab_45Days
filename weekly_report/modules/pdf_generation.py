"""
PDF Report Generation Module
==============================
Builds a professional, multi-section PDF using ReportLab Platypus.

Structure:
  1. Cover Page
  2. Executive Summary
  3. Weekly KPI Overview (cards)
  4. Revenue Trend Chart
  5. Project Status Summary
  6. Team Performance Highlights
  7. Upcoming Deadlines
  8. Key Observations & Recommendations
  9. Appendix — Detailed Tables
"""

import pandas as pd
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Image, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas as pdf_canvas

from config.settings import Config, OUTPUT_DIR
from config.logger import get_logger

log = get_logger(__name__)

PURPLE      = colors.HexColor(Config.BRAND_COLOR)
PURPLE_DARK = colors.HexColor("#3A1A6E")
PURPLE_PALE = colors.HexColor("#EDE7F6")
GOLD        = colors.HexColor("#F5A623")
GREEN       = colors.HexColor("#2ECC71")
RED         = colors.HexColor("#E74C3C")
GRAY        = colors.HexColor("#7F8C8D")
LIGHT_GRAY  = colors.HexColor("#F5F5F5")


# ─────────────────────────────────────────────
# Page numbering / footer canvas
# ─────────────────────────────────────────────
class NumberedCanvas(pdf_canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_states = []

    def showPage(self):
        self._saved_states.append(dict(self.__dict__))
        super().showPage()

    def save(self):
        num_pages = len(self._saved_states)
        for state in self._saved_states:
            self.__dict__.update(state)
            self._draw_footer(num_pages)
            super().showPage()
        super().save()

    def _draw_footer(self, total_pages):
        self.setFont("Helvetica", 8)
        self.setFillColor(GRAY)
        self.drawString(2 * cm, 1.2 * cm,
                         f"{Config.COMPANY_NAME} — Weekly Business Report")
        self.drawRightString(
            A4[0] - 2 * cm, 1.2 * cm,
            f"Page {self._pageNumber} of {total_pages}"
        )
        self.setStrokeColor(PURPLE_PALE)
        self.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)


# ─────────────────────────────────────────────
# Styles
# ─────────────────────────────────────────────
def get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        "CoverTitle", fontName="Helvetica-Bold", fontSize=30,
        textColor=colors.white, alignment=TA_CENTER, leading=36,
    ))
    styles.add(ParagraphStyle(
        "CoverSubtitle", fontName="Helvetica", fontSize=15,
        textColor=colors.white, alignment=TA_CENTER, leading=20, spaceBefore=10,
    ))
    styles.add(ParagraphStyle(
        "CoverMeta", fontName="Helvetica", fontSize=11,
        textColor=colors.HexColor("#E0D4F7"), alignment=TA_CENTER, leading=16,
    ))
    styles.add(ParagraphStyle(
        "SectionHeading", fontName="Helvetica-Bold", fontSize=16,
        textColor=PURPLE_DARK, spaceBefore=18, spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        "SubHeading", fontName="Helvetica-Bold", fontSize=12,
        textColor=PURPLE, spaceBefore=10, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "BodyJustify", fontName="Helvetica", fontSize=10.2,
        textColor=colors.HexColor("#333333"), leading=15, alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        "BulletText", fontName="Helvetica", fontSize=10.2,
        textColor=colors.HexColor("#333333"), leading=15, leftIndent=14,
    ))
    styles.add(ParagraphStyle(
        "KPILabel", fontName="Helvetica-Bold", fontSize=8.5,
        textColor=colors.HexColor("#666666"), alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "KPIValue", fontName="Helvetica-Bold", fontSize=18,
        textColor=PURPLE_DARK, alignment=TA_CENTER, spaceBefore=4,
    ))
    return styles


# ─────────────────────────────────────────────
# Section builders
# ─────────────────────────────────────────────
def build_cover_page(story, styles, week_start, week_end):
    cover_table_data = [[
        Paragraph(f"⚡ {Config.COMPANY_NAME}", styles["CoverTitle"]),
    ], [
        Paragraph("Weekly Business Report", styles["CoverSubtitle"]),
    ], [
        Paragraph(
            f"Reporting Period: {week_start.strftime('%d %B %Y')} – {week_end.strftime('%d %B %Y')}",
            styles["CoverMeta"]
        ),
    ], [
        Paragraph(
            f"Generated on {pd.Timestamp.now().strftime('%d %B %Y, %I:%M %p')}",
            styles["CoverMeta"]
        ),
    ]]

    cover_table = Table(cover_table_data, colWidths=[16 * cm], rowHeights=[80, 40, 30, 24])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PURPLE_DARK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, 0), 60),
    ]))

    story.append(Spacer(1, 4 * cm))
    story.append(cover_table)
    story.append(Spacer(1, 1.5 * cm))

    tagline = Paragraph(
        "<i>Executive Summary · Financial Performance · Project Delivery · "
        "Team Productivity · Operational Insights</i>",
        ParagraphStyle("Tagline", fontName="Helvetica-Oblique", fontSize=11,
                       textColor=PURPLE, alignment=TA_CENTER)
    )
    story.append(tagline)
    story.append(PageBreak())


def build_executive_summary(story, styles, kpis, week_start, week_end):
    story.append(Paragraph("Executive Summary", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", color=PURPLE_PALE, thickness=1))
    story.append(Spacer(1, 8))

    summary_text = (
        f"This report summarizes {Config.COMPANY_NAME}'s business performance for the week of "
        f"<b>{week_start.strftime('%d %B %Y')}</b> to <b>{week_end.strftime('%d %B %Y')}</b>. "
        f"During this period, the company generated <b>Rs.{kpis['total_revenue']:,.0f}</b> in revenue, "
        f"started <b>{kpis['new_projects_count']}</b> new project(s), and completed "
        f"<b>{kpis['completed_count']}</b> project(s). "
        f"The team collected <b>{kpis['invoices_paid_count']}</b> invoice payment(s) totalling "
        f"<b>Rs.{kpis['invoices_paid_amount']:,.0f}</b>, while <b>{kpis['overdue_count']}</b> tasks "
        f"remain overdue across active projects. "
        f"<b>{kpis['top_performer']}</b> was the top-performing team member this week, completing "
        f"<b>{kpis['top_performer_count']}</b> tasks. "
        f"Overall invoice collection rate stands at <b>{kpis['collection_rate']:.1f}%</b> and team "
        f"utilization for the week is <b>{kpis['utilization_rate']:.1f}%</b>."
    )
    story.append(Paragraph(summary_text, styles["BodyJustify"]))
    story.append(Spacer(1, 14))


def kpi_card_table(label, value, color, styles):
    data = [[Paragraph(label, styles["KPILabel"])],
            [Paragraph(value, styles["KPIValue"])]]
    t = Table(data, colWidths=[3.7 * cm], rowHeights=[22, 30])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 1, color),
        ("LINEBEFORE", (0, 0), (0, -1), 4, color),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def build_kpi_overview(story, styles, kpis):
    story.append(Paragraph("Weekly KPI Overview", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", color=PURPLE_PALE, thickness=1))
    story.append(Spacer(1, 10))

    cards = [
        kpi_card_table("REVENUE GENERATED", f"Rs.{kpis['total_revenue']/1e5:.1f}L", PURPLE, styles),
        kpi_card_table("NEW PROJECTS", str(kpis['new_projects_count']), GOLD, styles),
        kpi_card_table("PROJECTS COMPLETED", str(kpis['completed_count']), GREEN, styles),
        kpi_card_table("OVERDUE TASKS", str(kpis['overdue_count']), RED, styles),
    ]
    row1 = Table([cards], colWidths=[4 * cm] * 4)
    row1.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))

    cards2 = [
        kpi_card_table("INVOICES PAID", str(kpis['invoices_paid_count']), PURPLE, styles),
        kpi_card_table("COLLECTION RATE", f"{kpis['collection_rate']:.1f}%", GREEN, styles),
        kpi_card_table("TEAM UTILIZATION", f"{kpis['utilization_rate']:.1f}%", GOLD, styles),
        kpi_card_table("TOP PERFORMER", kpis['top_performer'].split()[0], PURPLE, styles),
    ]
    row2 = Table([cards2], colWidths=[4 * cm] * 4)
    row2.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))

    story.append(row1)
    story.append(Spacer(1, 10))
    story.append(row2)
    story.append(Spacer(1, 16))


def build_chart_section(story, styles, title, description, chart_path):
    story.append(Paragraph(title, styles["SubHeading"]))
    if description:
        story.append(Paragraph(description, styles["BodyJustify"]))
    story.append(Spacer(1, 6))
    if Path(chart_path).exists():
        story.append(Image(chart_path, width=15.5 * cm, height=15.5 * cm * 0.42))
    story.append(Spacer(1, 14))


def build_upcoming_deadlines(story, styles, upcoming_df):
    story.append(Paragraph("Upcoming Project Deadlines (Next 7 Days)", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", color=PURPLE_PALE, thickness=1))
    story.append(Spacer(1, 8))

    if upcoming_df.empty:
        story.append(Paragraph(
            "No project deadlines are scheduled in the upcoming 7 days.", styles["BodyJustify"]
        ))
        story.append(Spacer(1, 14))
        return

    table_data = [["Project", "Client", "Deadline", "Days Left"]]
    today = pd.Timestamp.now().normalize()
    for _, row in upcoming_df.head(12).iterrows():
        days_left = (row["Deadline"] - today).days
        table_data.append([
            str(row.get("Project Name", ""))[:34],
            str(row.get("Client Name", ""))[:18],
            row["Deadline"].strftime("%d %b %Y"),
            str(days_left),
        ])

    t = Table(table_data, colWidths=[7 * cm, 4.2 * cm, 3 * cm, 2.3 * cm])
    t.setStyle(_default_table_style())
    story.append(t)
    story.append(Spacer(1, 16))


def build_observations(story, styles, kpis):
    story.append(Paragraph("Key Observations & Recommendations", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", color=PURPLE_PALE, thickness=1))
    story.append(Spacer(1, 8))

    observations = []

    if kpis["overdue_count"] > 5:
        observations.append(
            f"<b>High overdue task volume:</b> {kpis['overdue_count']} tasks are currently overdue. "
            f"Recommend a weekly overdue-task triage meeting to re-assign or escalate stuck items."
        )
    else:
        observations.append(
            f"<b>Overdue tasks under control:</b> Only {kpis['overdue_count']} tasks are overdue, "
            f"indicating healthy task management this week."
        )

    if kpis["collection_rate"] < 70:
        observations.append(
            f"<b>Invoice collection needs attention:</b> Current collection rate is "
            f"{kpis['collection_rate']:.1f}%, below the 70% healthy threshold. Recommend "
            f"prioritizing follow-ups on outstanding invoices."
        )
    else:
        observations.append(
            f"<b>Healthy invoice collection:</b> Collection rate of {kpis['collection_rate']:.1f}% "
            f"reflects strong client payment discipline this period."
        )

    if kpis["utilization_rate"] > 100:
        observations.append(
            f"<b>Team over-utilization risk:</b> Utilization at {kpis['utilization_rate']:.1f}% "
            f"suggests possible burnout risk. Recommend reviewing workload distribution."
        )
    elif kpis["utilization_rate"] < 50:
        observations.append(
            f"<b>Spare team capacity available:</b> Utilization at {kpis['utilization_rate']:.1f}% "
            f"indicates room to take on additional project work this period."
        )
    else:
        observations.append(
            f"<b>Balanced team utilization:</b> Utilization at {kpis['utilization_rate']:.1f}% is "
            f"within the healthy operating range."
        )

    observations.append(
        f"<b>Top performer recognition:</b> {kpis['top_performer']} led the team with "
        f"{kpis['top_performer_count']} completed tasks this week — consider recognition in the "
        f"next team sync."
    )

    if not kpis["upcoming_deadlines"].empty:
        observations.append(
            f"<b>Upcoming deadline pressure:</b> {len(kpis['upcoming_deadlines'])} project(s) are "
            f"due within the next 7 days. Recommend a mid-week check-in on at-risk deliverables."
        )

    for obs in observations:
        story.append(Paragraph(f"• {obs}", styles["BulletText"]))
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 10))


def _default_table_style():
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ])


def build_appendix(story, styles, kpis):
    story.append(PageBreak())
    story.append(Paragraph("Appendix — Detailed Tables", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", color=PURPLE_PALE, thickness=1))
    story.append(Spacer(1, 10))

    # Projects started
    story.append(Paragraph("A.1 — Projects Started This Week", styles["SubHeading"]))
    df = kpis["proj_started_df"]
    if not df.empty:
        rows = [["Project", "Client", "Start Date", "Budget (Rs.)"]]
        for _, r in df.head(15).iterrows():
            rows.append([
                str(r.get("Project Name",""))[:30], str(r.get("Client Name",""))[:18],
                r["Start Date"].strftime("%d %b %Y") if pd.notna(r["Start Date"]) else "-",
                f"{r.get('Budget (INR)',0):,.0f}"
            ])
        t = Table(rows, colWidths=[6.5*cm, 4*cm, 3*cm, 3*cm])
        t.setStyle(_default_table_style())
        story.append(t)
    else:
        story.append(Paragraph("No new projects started this week.", styles["BodyJustify"]))
    story.append(Spacer(1, 14))

    # Projects completed
    story.append(Paragraph("A.2 — Projects Completed This Week", styles["SubHeading"]))
    df = kpis["proj_completed_df"]
    if not df.empty:
        rows = [["Project", "Client", "Completed On", "Amount Spent (Rs.)"]]
        for _, r in df.head(15).iterrows():
            rows.append([
                str(r.get("Project Name",""))[:30], str(r.get("Client Name",""))[:18],
                r["Actual End Date"].strftime("%d %b %Y") if pd.notna(r["Actual End Date"]) else "-",
                f"{r.get('Amount Spent (INR)',0):,.0f}"
            ])
        t = Table(rows, colWidths=[6.5*cm, 4*cm, 3*cm, 3*cm])
        t.setStyle(_default_table_style())
        story.append(t)
    else:
        story.append(Paragraph("No projects completed this week.", styles["BodyJustify"]))
    story.append(Spacer(1, 14))

    # Overdue tasks
    story.append(Paragraph("A.3 — Overdue Tasks", styles["SubHeading"]))
    df = kpis["overdue_tasks_df"]
    if not df.empty:
        rows = [["Project", "Assignee", "Priority", "Created Date"]]
        for _, r in df.head(20).iterrows():
            rows.append([
                str(r.get("Project Name",""))[:28], str(r.get("Assignee",""))[:16],
                str(r.get("Priority","")),
                r["Created Date"].strftime("%d %b %Y") if pd.notna(r["Created Date"]) else "-",
            ])
        t = Table(rows, colWidths=[6*cm, 4*cm, 2.5*cm, 3.5*cm])
        t.setStyle(_default_table_style())
        story.append(t)
    else:
        story.append(Paragraph("No overdue tasks. Great job!", styles["BodyJustify"]))
    story.append(Spacer(1, 14))

    # Invoices paid
    story.append(Paragraph("A.4 — Invoices Paid This Week", styles["SubHeading"]))
    df = kpis["invoices_paid_df"]
    if not df.empty:
        rows = [["Client", "Amount (Rs.)", "Paid Date", "Status"]]
        for _, r in df.head(15).iterrows():
            rows.append([
                str(r.get("Client Name",""))[:22],
                f"{r.get('Invoice Amount (INR)',0):,.0f}",
                r["Paid Date"].strftime("%d %b %Y") if pd.notna(r["Paid Date"]) else "-",
                str(r.get("Payment Status","")),
            ])
        t = Table(rows, colWidths=[5*cm, 3.5*cm, 3.5*cm, 4*cm])
        t.setStyle(_default_table_style())
        story.append(t)
    else:
        story.append(Paragraph("No invoices were paid this week.", styles["BodyJustify"]))


# ─────────────────────────────────────────────
# Main builder
# ─────────────────────────────────────────────
def generate_pdf_report(kpis: dict, charts: dict, week_start: pd.Timestamp, week_end: pd.Timestamp) -> str:
    """Builds the full PDF and returns its file path."""
    filename = f"YoungXCode_Weekly_Report_{week_start.strftime('%Y%m%d')}.pdf"
    filepath = str(OUTPUT_DIR / filename)

    log.info(f"Building PDF report: {filepath}")

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        topMargin=2 * cm, bottomMargin=2 * cm,
        leftMargin=2 * cm, rightMargin=2 * cm,
        title=f"{Config.COMPANY_NAME} Weekly Business Report",
        author=Config.COMPANY_NAME,
    )

    styles = get_styles()
    story = []

    build_cover_page(story, styles, week_start, week_end)
    build_executive_summary(story, styles, kpis, week_start, week_end)
    build_kpi_overview(story, styles, kpis)

    build_chart_section(
        story, styles, "Revenue Trend",
        "Weekly revenue collected over the last 8 weeks, based on paid invoices.",
        charts["revenue_trend"]
    )
    build_chart_section(
        story, styles, "Project Status Summary",
        "Current distribution of all projects across status categories.",
        charts["project_status"]
    )
    build_chart_section(
        story, styles, "Team Performance Highlights",
        "Tasks completed by each team member during the reporting week.",
        charts["team_performance"]
    )
    build_chart_section(
        story, styles, "Invoice Collection Summary",
        "Overall invoice collection rate across all clients to date.",
        charts["invoice_collection"]
    )

    build_upcoming_deadlines(story, styles, kpis["upcoming_deadlines"])
    build_observations(story, styles, kpis)
    build_appendix(story, styles, kpis)

    doc.build(story, canvasmaker=NumberedCanvas)
    log.info(f"PDF report generated successfully: {filepath}")
    return filepath
