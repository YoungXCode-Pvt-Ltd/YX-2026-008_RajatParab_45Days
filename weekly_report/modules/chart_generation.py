"""
Chart Generation Module
=========================
Generates branded PNG charts (matplotlib) used inside the PDF report.
All charts are saved to /output/charts and return their file path.
"""

import matplotlib
matplotlib.use("Agg")  # headless rendering, safe for servers/cron
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from pathlib import Path

from config.settings import Config, OUTPUT_DIR
from config.logger import get_logger

log = get_logger(__name__)

CHART_DIR = OUTPUT_DIR / "charts"
CHART_DIR.mkdir(exist_ok=True)

PURPLE      = Config.BRAND_COLOR
PURPLE_2    = Config.BRAND_COLOR_2
GOLD        = "#F5A623"
GREEN       = "#2ECC71"
RED         = "#E74C3C"
GRAY        = "#7F8C8D"

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor":   "#FAFAFA",
    "axes.edgecolor":   "#DDDDDD",
    "axes.grid":        True,
    "grid.alpha":       0.3,
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "font.family":      "DejaVu Sans",
})


def revenue_trend_chart(trend_df: pd.DataFrame) -> str:
    """Bar chart of weekly revenue for the last N weeks."""
    path = CHART_DIR / "revenue_trend.png"
    if trend_df.empty:
        _empty_chart(path, "No revenue data available")
        return str(path)

    fig, ax = plt.subplots(figsize=(8, 3.4))
    bars = ax.bar(trend_df["week_label"], trend_df["revenue"] / 1e5,
                   color=PURPLE, edgecolor="white", width=0.6)
    for bar, val in zip(bars, trend_df["revenue"]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f"₹{val/1e5:.1f}L", ha="center", va="bottom", fontsize=8, fontweight="bold")
    ax.set_ylabel("Revenue (₹ Lakhs)", fontsize=10)
    ax.set_title("Revenue Trend — Last 8 Weeks", fontsize=12, fontweight="bold", color=PURPLE)
    plt.xticks(rotation=30, ha="right", fontsize=8)
    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info(f"Revenue trend chart saved: {path}")
    return str(path)


def project_status_chart(status_df: pd.DataFrame) -> str:
    """Donut chart of project status distribution."""
    path = CHART_DIR / "project_status.png"
    if status_df.empty:
        _empty_chart(path, "No project status data available")
        return str(path)

    STATUS_COLORS = {
        "Completed":   GREEN,
        "In Progress": PURPLE,
        "On Hold":     GOLD,
        "Delayed":     RED,
        "Cancelled":   GRAY,
    }
    colors = [STATUS_COLORS.get(s, "#3498DB") for s in status_df["Status"]]

    fig, ax = plt.subplots(figsize=(5, 4))
    wedges, texts, autotexts = ax.pie(
        status_df["Count"], labels=status_df["Status"], autopct="%1.0f%%",
        colors=colors, startangle=90, pctdistance=0.78,
        wedgeprops=dict(width=0.42, edgecolor="white", linewidth=2)
    )
    for at in autotexts:
        at.set_fontsize(9); at.set_fontweight("bold"); at.set_color("white")
    for t in texts:
        t.set_fontsize(9)
    ax.set_title("Project Status Distribution", fontsize=12, fontweight="bold", color=PURPLE)
    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info(f"Project status chart saved: {path}")
    return str(path)


def team_performance_chart(perf_df: pd.DataFrame) -> str:
    """Horizontal bar chart: tasks completed per team member this week."""
    path = CHART_DIR / "team_performance.png"
    if perf_df.empty:
        _empty_chart(path, "No team activity data available")
        return str(path)

    perf_sorted = perf_df.sort_values("tasks_completed", ascending=True).tail(10)

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(perf_sorted["Assignee"], perf_sorted["tasks_completed"],
                   color=PURPLE, edgecolor="white", height=0.6)
    for bar, val in zip(bars, perf_sorted["tasks_completed"]):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                str(int(val)), va="center", fontsize=9, fontweight="bold")
    ax.set_xlabel("Tasks Completed (This Week)", fontsize=10)
    ax.set_title("Team Performance — Tasks Completed", fontsize=12, fontweight="bold", color=PURPLE)
    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info(f"Team performance chart saved: {path}")
    return str(path)


def invoice_collection_chart(collection_rate: float, paid_amt: float, total_amt: float) -> str:
    """Gauge-style horizontal bar showing invoice collection rate."""
    path = CHART_DIR / "invoice_collection.png"

    fig, ax = plt.subplots(figsize=(8, 1.8))
    ax.barh([0], [100], color="#E8E8E8", height=0.5)
    color = GREEN if collection_rate >= 75 else GOLD if collection_rate >= 50 else RED
    ax.barh([0], [collection_rate], color=color, height=0.5)
    ax.text(collection_rate + 2, 0, f"{collection_rate:.1f}%",
            va="center", fontsize=13, fontweight="bold", color=color)
    ax.set_xlim(0, 115)
    ax.set_yticks([])
    ax.set_xlabel(f"Collected ₹{paid_amt/1e5:.1f}L of ₹{total_amt/1e5:.1f}L Total Invoiced", fontsize=9)
    ax.set_title("Invoice Collection Rate", fontsize=12, fontweight="bold", color=PURPLE)
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info(f"Invoice collection chart saved: {path}")
    return str(path)


def _empty_chart(path: Path, message: str):
    """Placeholder chart for empty datasets so the PDF never breaks."""
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=12, color=GRAY)
    ax.axis("off")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def generate_all_charts(kpis: dict, week_data: dict, today: pd.Timestamp) -> dict:
    """Convenience wrapper: generates every chart needed for the report."""
    from modules.kpi_calculations import (
        revenue_trend_last_n_weeks, project_status_breakdown, team_performance_table
    )

    log.info("Generating all report charts...")

    trend_df  = revenue_trend_last_n_weeks(week_data["all_invoices"], today)
    status_df = project_status_breakdown(week_data["all_projects"])
    perf_df   = team_performance_table(week_data["all_tasks"], today)

    paid_total  = week_data["all_invoices"][
        week_data["all_invoices"]["Payment Status"] == "Paid"
    ]["Invoice Amount (INR)"].sum()
    total_total = week_data["all_invoices"]["Invoice Amount (INR)"].sum()

    charts = {
        "revenue_trend":      revenue_trend_chart(trend_df),
        "project_status":     project_status_chart(status_df),
        "team_performance":   team_performance_chart(perf_df),
        "invoice_collection": invoice_collection_chart(kpis["collection_rate"], paid_total, total_total),
    }
    log.info("All charts generated successfully.")
    return charts
