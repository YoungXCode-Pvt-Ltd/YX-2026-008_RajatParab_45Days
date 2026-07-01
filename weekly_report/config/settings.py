"""
YoungXCode Weekly Business Report — Configuration
====================================================
All sensitive settings are loaded from environment variables.
Create a `.env` file (see .env.example) or export these in your
server/cron environment before running run_scheduler.py.
"""

import os
from pathlib import Path

# Optional: load a local .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


BASE_DIR   = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR    = BASE_DIR / "logs"
ASSET_DIR  = BASE_DIR / "assets"

OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
ASSET_DIR.mkdir(exist_ok=True)


class Config:
    # ── Company branding ──
    COMPANY_NAME  = os.getenv("COMPANY_NAME", "YoungXCode")
    BRAND_COLOR   = os.getenv("BRAND_COLOR", "#5B2D8E")     # Purple
    BRAND_COLOR_2 = os.getenv("BRAND_COLOR_2", "#7B4DB8")
    LOGO_PATH     = os.getenv("LOGO_PATH", str(ASSET_DIR / "logo.png"))

    # ── Data source ──
    # "excel" | "csv" | "api"  — controls which loader is used in data_extraction.py
    DATA_SOURCE   = os.getenv("DATA_SOURCE", "excel")
    DATA_FILE     = os.getenv("DATA_FILE", str(BASE_DIR / "YoungXCode_BusinessDataset.xlsx"))
    CSV_DIR       = os.getenv("CSV_DIR", str(BASE_DIR / "data_csv"))
    API_BASE_URL  = os.getenv("API_BASE_URL", "")
    API_KEY       = os.getenv("API_KEY", "")

    # ── Email / SMTP (Gmail) ──
    SMTP_SERVER   = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
    SMTP_EMAIL    = os.getenv("SMTP_EMAIL", "")          # sender Gmail address
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")       # Gmail App Password (NOT your normal password)
    EMAIL_RECIPIENTS = [
        e.strip() for e in os.getenv("EMAIL_RECIPIENTS", "").split(",") if e.strip()
    ]
    EMAIL_SUBJECT_TEMPLATE = os.getenv(
        "EMAIL_SUBJECT_TEMPLATE",
        "📊 {company} Weekly Business Report — Week of {week_start} to {week_end}"
    )

    # ── Scheduling ──
    SCHEDULE_DAY  = os.getenv("SCHEDULE_DAY", "monday").lower()   # day of week
    SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "09:00")           # 24h HH:MM

    # ── Report behaviour ──
    OVERDUE_THRESHOLD_DAYS = int(os.getenv("OVERDUE_THRESHOLD_DAYS", "0"))
    UPCOMING_DEADLINE_DAYS = int(os.getenv("UPCOMING_DEADLINE_DAYS", "7"))
    AVAILABLE_HOURS_PER_PERSON_WEEK = int(os.getenv("AVAILABLE_HOURS_PER_PERSON_WEEK", "40"))

    @classmethod
    def validate(cls):
        """Raise a clear error if mandatory settings are missing before sending email."""
        missing = []
        if not cls.SMTP_EMAIL:
            missing.append("SMTP_EMAIL")
        if not cls.SMTP_PASSWORD:
            missing.append("SMTP_PASSWORD")
        if not cls.EMAIL_RECIPIENTS:
            missing.append("EMAIL_RECIPIENTS")
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}. "
                f"See .env.example for setup instructions."
            )
