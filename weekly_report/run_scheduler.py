"""
run_scheduler.py
==================
Runs continuously (on a server, VM, or background process) and triggers
the weekly report job every Monday at 09:00 (configurable via .env).

Usage:
    python run_scheduler.py

Recommended deployment:
    - Run inside `screen`, `tmux`, or as a systemd service / supervisor process
      so it keeps running after you disconnect.
    - See README.md for a sample systemd unit file.
"""

import schedule
import time
import sys

from config.settings import Config
from config.logger import get_logger
from generate_report import run_weekly_report_job

log = get_logger("scheduler")


def job():
    log.info("Scheduled trigger fired — starting weekly report job.")
    result = run_weekly_report_job(send_email=True)
    if result["success"] and result["email_sent"]:
        log.info("Scheduled job completed: report generated and emailed successfully.")
    elif result["success"] and not result["email_sent"]:
        log.warning("Scheduled job completed: report generated but EMAIL DELIVERY FAILED. "
                    "Check SMTP settings and logs above.")
    else:
        log.error(f"Scheduled job FAILED: {result['error']}")


def configure_schedule():
    """Reads Config.SCHEDULE_DAY / SCHEDULE_TIME and wires up the `schedule` job."""
    day = Config.SCHEDULE_DAY.lower()
    time_str = Config.SCHEDULE_TIME

    day_map = {
        "monday":    schedule.every().monday,
        "tuesday":   schedule.every().tuesday,
        "wednesday": schedule.every().wednesday,
        "thursday":  schedule.every().thursday,
        "friday":    schedule.every().friday,
        "saturday":  schedule.every().saturday,
        "sunday":    schedule.every().sunday,
    }

    if day not in day_map:
        log.error(f"Invalid SCHEDULE_DAY '{day}'. Defaulting to monday.")
        day = "monday"

    day_map[day].at(time_str).do(job)
    log.info(f"Scheduler configured: weekly report will run every "
              f"{day.capitalize()} at {time_str}.")


def main():
    log.info("=" * 60)
    log.info(f"{Config.COMPANY_NAME} WEEKLY REPORT SCHEDULER STARTING")
    log.info("=" * 60)

    configure_schedule()

    log.info("Scheduler is now running. Waiting for next scheduled run...")
    log.info("Press Ctrl+C to stop.")

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # check every 30 seconds — light on CPU, precise enough
    except KeyboardInterrupt:
        log.info("Scheduler stopped manually (KeyboardInterrupt).")
        sys.exit(0)
    except Exception as e:
        log.error(f"Scheduler crashed unexpectedly: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
