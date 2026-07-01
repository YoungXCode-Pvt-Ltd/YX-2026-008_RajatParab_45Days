"""
Data Extraction Module
=======================
Loads raw business data (Excel / CSV / API) and returns clean,
typed Pandas DataFrames ready for KPI calculation.

Supports three interchangeable sources controlled by Config.DATA_SOURCE:
    - "excel" : single workbook with Clients / Projects / Tasks / Invoices sheets
    - "csv"   : a folder containing clients.csv, projects.csv, tasks.csv, invoices.csv
    - "api"   : REST endpoints returning the same four datasets as JSON
"""

import pandas as pd
import requests
from pathlib import Path

from config.settings import Config
from config.logger import get_logger

log = get_logger(__name__)


def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.strip()
    return df


def load_from_excel(path: str) -> dict:
    log.info(f"Loading data from Excel workbook: {path}")
    clients  = _clean_columns(pd.read_excel(path, sheet_name="Clients"))
    projects = _clean_columns(pd.read_excel(path, sheet_name="Projects"))
    tasks    = _clean_columns(pd.read_excel(path, sheet_name="Tasks"))
    invoices = _clean_columns(pd.read_excel(path, sheet_name="Invoices"))
    return {"clients": clients, "projects": projects, "tasks": tasks, "invoices": invoices}


def load_from_csv(folder: str) -> dict:
    log.info(f"Loading data from CSV folder: {folder}")
    folder = Path(folder)
    clients  = _clean_columns(pd.read_csv(folder / "clients.csv"))
    projects = _clean_columns(pd.read_csv(folder / "projects.csv"))
    tasks    = _clean_columns(pd.read_csv(folder / "tasks.csv"))
    invoices = _clean_columns(pd.read_csv(folder / "invoices.csv"))
    return {"clients": clients, "projects": projects, "tasks": tasks, "invoices": invoices}


def load_from_api(base_url: str, api_key: str) -> dict:
    log.info(f"Loading data from API: {base_url}")
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    def _get(endpoint):
        resp = requests.get(f"{base_url.rstrip('/')}/{endpoint}", headers=headers, timeout=30)
        resp.raise_for_status()
        return _clean_columns(pd.DataFrame(resp.json()))

    return {
        "clients":  _get("clients"),
        "projects": _get("projects"),
        "tasks":    _get("tasks"),
        "invoices": _get("invoices"),
    }


def load_raw_data() -> dict:
    """Dispatch to the correct loader based on Config.DATA_SOURCE."""
    source = Config.DATA_SOURCE.lower()
    try:
        if source == "excel":
            data = load_from_excel(Config.DATA_FILE)
        elif source == "csv":
            data = load_from_csv(Config.CSV_DIR)
        elif source == "api":
            data = load_from_api(Config.API_BASE_URL, Config.API_KEY)
        else:
            raise ValueError(f"Unknown DATA_SOURCE '{source}'. Use excel, csv, or api.")
    except Exception as e:
        log.error(f"Data extraction failed: {e}")
        raise

    return _typecast(data)


def _typecast(data: dict) -> dict:
    """Ensure dates and numeric fields are correctly typed across all sheets."""
    clients, projects, tasks, invoices = (
        data["clients"], data["projects"], data["tasks"], data["invoices"]
    )

    if "Join Date" in clients.columns:
        clients["Join Date"] = pd.to_datetime(clients["Join Date"], dayfirst=True, errors="coerce")

    for col in ["Start Date", "Deadline", "Actual End Date"]:
        if col in projects.columns:
            projects[col] = pd.to_datetime(projects[col], errors="coerce")
    for col in ["Budget (INR)", "Amount Spent (INR)"]:
        if col in projects.columns:
            projects[col] = pd.to_numeric(projects[col], errors="coerce")

    for col in ["Created Date", "Completed Date"]:
        if col in tasks.columns:
            tasks[col] = pd.to_datetime(tasks[col], errors="coerce")
    for col in ["Estimated Hours", "Actual Hours"]:
        if col in tasks.columns:
            tasks[col] = pd.to_numeric(tasks[col], errors="coerce")

    for col in ["Due Date", "Paid Date"]:
        if col in invoices.columns:
            invoices[col] = pd.to_datetime(invoices[col], errors="coerce")
    for col in ["Invoice Amount (INR)", "GST (INR)"]:
        if col in invoices.columns:
            invoices[col] = pd.to_numeric(invoices[col], errors="coerce")

    log.info(
        f"Data loaded — Clients: {len(clients)}, Projects: {len(projects)}, "
        f"Tasks: {len(tasks)}, Invoices: {len(invoices)}"
    )
    return {"clients": clients, "projects": projects, "tasks": tasks, "invoices": invoices}


def filter_week(data: dict, week_start: pd.Timestamp, week_end: pd.Timestamp) -> dict:
    """Return a dict of DataFrames filtered to the reporting week (Mon-Sun)."""
    projects = data["projects"]
    tasks    = data["tasks"]
    invoices = data["invoices"]

    week_projects_started   = projects[projects["Start Date"].between(week_start, week_end)]
    week_projects_completed = projects[projects["Actual End Date"].between(week_start, week_end)]
    week_tasks              = tasks[tasks["Created Date"].between(week_start, week_end)]
    week_invoices_paid      = invoices[invoices["Paid Date"].between(week_start, week_end)]

    return {
        "projects_started":   week_projects_started,
        "projects_completed": week_projects_completed,
        "tasks_this_week":    week_tasks,
        "invoices_paid":      week_invoices_paid,
        "all_projects":       projects,
        "all_tasks":          tasks,
        "all_invoices":       invoices,
        "all_clients":        data["clients"],
    }
