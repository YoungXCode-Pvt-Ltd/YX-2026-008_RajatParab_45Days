"""
Main Orchestrator — generate_report.py
=========================================
Coordinates the full weekly report pipeline:
  1. Extract data
  2. Filter to reporting week
  3. Calculate KPIs
  4. Generate charts
  5. Build PDF
  6. Send email

Can be run directly for a one-off report (e.g. testing, manual trigger),
or imported and called by run_scheduler.py every Monday at 09:00.
"""

import sys
import pandas as pd
import traceback

from config.logger import get_logger
from modules.data_extraction import load_raw_data, filter_week
from modules.kpi_calculations import calculate_kpis
from modules.chart_generation import generate_all_charts
from modules.pdf_generation import generate_pdf_report
from modules.email_delivery import send_email_with_attachment

log = get_logger("generate_report")


def get_reporting_week(reference_date: pd.Timestamp = None):
    """
    Returns (week_start, week_end) for the PREVIOUS Mon-Sun week,
    relative to reference_date (defaults to now).
    Used when the scheduler fires on Monday morning to report on
    the week that just ended.
    """
    if reference_date is None:
        reference_date = pd.Timestamp.now()

    # Most recent Monday (could be today if reference_date is Monday)
    this_monday = reference_date - pd.Timedelta(days=reference_date.weekday())
    this_monday = this_monday.normalize()

    week_start = this_monday - pd.Timedelta(days=7)   # previous Monday
    week_end   = this_monday - pd.Timedelta(seconds=1)  # previous Sunday 23:59:59

    return week_start, week_end


def run_weekly_report_job(send_email: bool = True) -> dict:
    """
    Full pipeline. Returns a result dict with status info for logging/testing.
    Designed to never raise — all errors are caught and logged so a single
    failed run doesn't crash the scheduler process.
    """
    result = {"success": False, "pdf_path": None, "email_sent": False, "error": None}

    try:
        log.info("=" * 60)
        log.info("STARTING WEEKLY REPORT GENERATION JOB")
        log.info("=" * 60)

        today = pd.Timestamp.now()
        week_start, week_end = get_reporting_week(today)
        log.info(f"Reporting week: {week_start.date()} to {week_end.date()}")

        # 1. Extract
        raw_data = load_raw_data()

        # 2. Filter to week
        week_data = filter_week(raw_data, week_start, week_end)

        # 3. KPIs
        kpis = calculate_kpis(week_data, today)

        # 4. Charts
        charts = generate_all_charts(kpis, week_data, today)

        # 5. PDF
        pdf_path = generate_pdf_report(kpis, charts, week_start, week_end)
        result["pdf_path"] = pdf_path

        # 6. Email
        if send_email:
            email_ok = send_email_with_attachment(pdf_path, kpis, week_start, week_end)
            result["email_sent"] = email_ok
            if not email_ok:
                log.warning("Report generated but email delivery failed. PDF is still available on disk.")
        else:
            log.info("send_email=False — skipping delivery (report saved locally only).")

        result["success"] = True
        log.info("WEEKLY REPORT JOB COMPLETED SUCCESSFULLY")
        log.info("=" * 60)

    except Exception as e:
        log.error(f"WEEKLY REPORT JOB FAILED: {e}")
        log.error(traceback.format_exc())
        result["error"] = str(e)

    return result


if __name__ == "__main__":
    # Manual / one-off run: `python generate_report.py` or
    # `python generate_report.py --no-email` to skip sending.
    send = "--no-email" not in sys.argv
    outcome = run_weekly_report_job(send_email=send)

    if outcome["success"]:
        print(f"\nReport generated: {outcome['pdf_path']}")
        print(f"Email sent: {outcome['email_sent']}")
        sys.exit(0)
    else:
        print(f"\nReport generation FAILED: {outcome['error']}")
        sys.exit(1)
