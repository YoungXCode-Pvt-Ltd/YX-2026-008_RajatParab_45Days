"""
KPI Calculation Module
========================
Pure functions that turn filtered weekly data into the metrics
required for the Weekly Business Report.
"""

import pandas as pd
from config.settings import Config
from config.logger import get_logger

log = get_logger(__name__)


def calculate_kpis(week_data: dict, today: pd.Timestamp) -> dict:
    """Compute all headline KPIs for the report. Returns a flat dict."""
    log.info("Calculating weekly KPIs...")

    all_projects = week_data["all_projects"]
    all_tasks    = week_data["all_tasks"]
    all_invoices = week_data["all_invoices"]

    proj_started   = week_data["projects_started"]
    proj_completed = week_data["projects_completed"]
    invoices_paid  = week_data["invoices_paid"]
    tasks_week     = week_data["tasks_this_week"]

    # ── Revenue generated this week (sum of invoices paid in window) ──
    total_revenue = invoices_paid["Invoice Amount (INR)"].sum()

    # ── New projects started ──
    new_projects_count = len(proj_started)

    # ── Projects completed ──
    completed_count = len(proj_completed)

    # ── Overdue tasks (not completed, created before today, age > threshold) ──
    overdue_mask = (
        all_tasks["Completed Date"].isna() &
        ((today - all_tasks["Created Date"]).dt.days > (30 + Config.OVERDUE_THRESHOLD_DAYS))
    )
    overdue_tasks_df = all_tasks[overdue_mask]
    overdue_count = len(overdue_tasks_df)

    # ── Invoices paid (count + amount) ──
    invoices_paid_count  = len(invoices_paid)
    invoices_paid_amount = invoices_paid["Invoice Amount (INR)"].sum()

    # ── Top performing team member (most tasks completed this week) ──
    completed_tasks_week = all_tasks[
        all_tasks["Completed Date"].between(
            today - pd.Timedelta(days=7), today
        )
    ]
    if not completed_tasks_week.empty:
        top_performer_series = completed_tasks_week["Assignee"].value_counts()
        top_performer = top_performer_series.index[0]
        top_performer_count = int(top_performer_series.iloc[0])
    else:
        top_performer, top_performer_count = "N/A", 0

    # ── Upcoming deadlines (current week, next N days) ──
    deadline_window_end = today + pd.Timedelta(days=Config.UPCOMING_DEADLINE_DAYS)
    upcoming_deadlines = all_projects[
        all_projects["Deadline"].between(today, deadline_window_end) &
        all_projects["Actual End Date"].isna()
    ].sort_values("Deadline")

    # ── Invoice Collection Rate (overall, not just this week) ──
    paid_total  = all_invoices[all_invoices["Payment Status"] == "Paid"]["Invoice Amount (INR)"].sum()
    total_total = all_invoices["Invoice Amount (INR)"].sum()
    collection_rate = (paid_total / total_total * 100) if total_total > 0 else 0

    # ── Team utilization this week ──
    n_members  = all_tasks["Assignee"].nunique()
    avail_hrs  = n_members * Config.AVAILABLE_HOURS_PER_PERSON_WEEK
    actual_hrs = tasks_week["Actual Hours"].dropna().sum()
    utilization_rate = (actual_hrs / avail_hrs * 100) if avail_hrs > 0 else 0

    kpis = {
        "total_revenue":        total_revenue,
        "new_projects_count":   new_projects_count,
        "completed_count":      completed_count,
        "overdue_count":        overdue_count,
        "overdue_tasks_df":     overdue_tasks_df,
        "invoices_paid_count":  invoices_paid_count,
        "invoices_paid_amount": invoices_paid_amount,
        "top_performer":        top_performer,
        "top_performer_count":  top_performer_count,
        "upcoming_deadlines":   upcoming_deadlines,
        "collection_rate":      collection_rate,
        "utilization_rate":     utilization_rate,
        "proj_started_df":      proj_started,
        "proj_completed_df":    proj_completed,
        "invoices_paid_df":     invoices_paid,
    }

    log.info(
        f"KPIs computed — Revenue: Rs.{total_revenue:,.0f}, New Projects: {new_projects_count}, "
        f"Completed: {completed_count}, Overdue: {overdue_count}, Top Performer: {top_performer}"
    )
    return kpis


def revenue_trend_last_n_weeks(all_invoices: pd.DataFrame, today: pd.Timestamp, n_weeks: int = 8) -> pd.DataFrame:
    """Weekly revenue (paid invoices) for the last N weeks, for the trend chart."""
    start = today - pd.Timedelta(weeks=n_weeks)
    window = all_invoices[
        all_invoices["Paid Date"].between(start, today) &
        (all_invoices["Payment Status"] == "Paid")
    ].copy()

    if window.empty:
        return pd.DataFrame(columns=["week_label", "revenue"])

    window["week"] = window["Paid Date"].dt.to_period("W").apply(lambda r: r.start_time)
    trend = window.groupby("week")["Invoice Amount (INR)"].sum().reset_index()
    trend.columns = ["week", "revenue"]
    trend["week_label"] = trend["week"].dt.strftime("%d %b")
    return trend


def project_status_breakdown(all_projects: pd.DataFrame) -> pd.DataFrame:
    counts = all_projects["Project Status"].value_counts().reset_index()
    counts.columns = ["Status", "Count"]
    return counts


def team_performance_table(all_tasks: pd.DataFrame, today: pd.Timestamp) -> pd.DataFrame:
    """Per-member completed tasks and hours for the current week."""
    week_start = today - pd.Timedelta(days=7)
    week_tasks = all_tasks[all_tasks["Created Date"].between(week_start, today)]

    perf = week_tasks.groupby("Assignee").agg(
        tasks_assigned = ("Project Name", "count"),
        tasks_completed= ("Completed Date", lambda x: x.notna().sum()),
        hours_logged   = ("Actual Hours", lambda x: x.dropna().sum()),
    ).reset_index().sort_values("tasks_completed", ascending=False)

    return perf
