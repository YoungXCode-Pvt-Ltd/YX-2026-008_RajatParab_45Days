# YoungXCode — Weekly Business Report Automation

Fully automated Python system that generates a branded PDF business report
every **Monday at 09:00** and emails it to management via Gmail.

---

## Project Structure

```
weekly_report/
├── config/
│   ├── settings.py        # All configuration (reads from .env)
│   └── logger.py          # Centralized logging setup
├── modules/
│   ├── data_extraction.py # Loads data (Excel / CSV / API)
│   ├── kpi_calculations.py# Computes all KPIs
│   ├── chart_generation.py# Matplotlib charts -> PNG
│   ├── pdf_generation.py  # ReportLab PDF builder
│   └── email_delivery.py  # smtplib Gmail sender
├── output/                # Generated PDFs + chart PNGs land here
├── logs/                  # Rotating log files
├── assets/                # Logo / static assets
├── generate_report.py     # Main orchestrator (run once manually)
├── run_scheduler.py       # Continuous scheduler (Monday 09:00)
├── .env.example           # Copy to .env and fill in your values
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment variables
```bash
cp .env.example .env
nano .env     # fill in your real values
```

**Gmail App Password (required):**
Gmail blocks regular password login for SMTP. You must generate an
App Password:
1. Enable 2-Step Verification on the Gmail account ->
   https://myaccount.google.com/security
2. Generate an App Password ->
   https://myaccount.google.com/apppasswords
3. Paste the 16-character password into `SMTP_PASSWORD` in `.env`

### 3. Provide your data
Place `YoungXCode_BusinessDataset.xlsx` (with `Clients`, `Projects`,
`Tasks`, `Invoices` sheets) in the project root, or point `DATA_FILE`
in `.env` to its location. CSV and API sources are also supported
(set `DATA_SOURCE=csv` or `DATA_SOURCE=api`).

---

## Running

### One-off manual report (for testing)
```bash
python generate_report.py            # generates PDF + sends email
python generate_report.py --no-email # generates PDF only, skips email
```

### Continuous scheduler (production)
```bash
python run_scheduler.py
```
This process must keep running for the Monday 09:00 trigger to fire.
Do not run it in a terminal you plan to close — use one of the options below.

---

## Production Deployment Options

### Option A — systemd service (recommended for Linux servers)
Create `/etc/systemd/system/youngxcode-report.service`:
```ini
[Unit]
Description=YoungXCode Weekly Report Scheduler
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/weekly_report
ExecStart=/usr/bin/python3 /opt/weekly_report/run_scheduler.py
Restart=always
RestartSec=10
EnvironmentFile=/opt/weekly_report/.env

[Install]
WantedBy=multi-user.target
```
Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable youngxcode-report
sudo systemctl start youngxcode-report
sudo systemctl status youngxcode-report
```

### Option B — tmux / screen (quick & simple)
```bash
tmux new -s weekly_report
python run_scheduler.py
# Ctrl+B then D to detach -- keeps running after you disconnect
```

### Option C — Cron (alternative to `schedule`)
If you prefer not to keep a process running continuously:
```bash
crontab -e
# Add this line (Monday 09:00):
0 9 * * 1 cd /opt/weekly_report && /usr/bin/python3 generate_report.py >> logs/cron.log 2>&1
```

---

## Sample Report Structure

1. Cover Page — "Weekly Business Report – YoungXCode" with reporting dates
2. Executive Summary — narrative paragraph summarizing the week
3. Weekly KPI Overview — 8 KPI cards (Revenue, New Projects, Completed,
   Overdue, Invoices Paid, Collection Rate, Utilization, Top Performer)
4. Revenue Trend Chart — last 8 weeks
5. Project Status Summary — donut chart
6. Team Performance Highlights — bar chart, tasks completed per member
7. Invoice Collection Summary — collection rate gauge
8. Upcoming Deadlines — table of projects due in next 7 days
9. Key Observations & Recommendations — auto-generated insights
10. Appendix — detailed tables (projects started/completed, overdue
    tasks, invoices paid)

---

## Configuration Reference (.env)

| Variable | Description | Default |
|---|---|---|
| `COMPANY_NAME` | Brand name on report | YoungXCode |
| `BRAND_COLOR` | Primary hex color | #5B2D8E |
| `DATA_SOURCE` | excel / csv / api | excel |
| `DATA_FILE` | Path to Excel workbook | — |
| `SMTP_EMAIL` | Sender Gmail address | — |
| `SMTP_PASSWORD` | Gmail App Password | — |
| `EMAIL_RECIPIENTS` | Comma-separated recipient list | — |
| `SCHEDULE_DAY` | Day of week to run | monday |
| `SCHEDULE_TIME` | 24h HH:MM | 09:00 |
| `UPCOMING_DEADLINE_DAYS` | Lookahead window for deadlines | 7 |

---

## Logging

All activity is logged to `logs/weekly_report.log` (rotating, 5MB x 5 files)
and printed to console. Each run logs:
- Data extraction status (row counts per sheet)
- KPI calculation results
- Chart generation confirmations
- PDF build confirmation
- Email delivery attempts, retries, and final status
- Any errors with full stack traces

---

## Error Handling

- The scheduler never crashes on a failed report — errors are caught,
  logged, and the scheduler waits for the next trigger.
- Email delivery retries up to 3 times with backoff for transient SMTP
  errors (timeouts, connection drops). Authentication errors fail fast
  with a clear message (likely wrong App Password).
- Empty datasets (no overdue tasks, no deadlines, no revenue) render
  graceful "No data" placeholders instead of breaking the PDF.

---

## Testing Checklist Before Going Live

- [ ] `.env` filled in with real SMTP credentials and recipient list
- [ ] `python generate_report.py --no-email` runs without errors
- [ ] Generated PDF in `output/` looks correct
- [ ] `python generate_report.py` successfully sends a test email
- [ ] Scheduler started via systemd/tmux and left running
- [ ] Logs show "Scheduler configured: weekly report will run every Monday at 09:00"
