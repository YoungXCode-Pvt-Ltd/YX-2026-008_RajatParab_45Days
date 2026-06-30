"""
YoungXCode Management Dashboard
Brand Color: Purple (#5B2D8E)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import os

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="YoungXCode Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# BRAND THEME
# ─────────────────────────────────────────────
PURPLE      = "#5B2D8E"
PURPLE_LIGHT= "#7B4DB8"
PURPLE_PALE = "#EDE7F6"
PURPLE_DARK = "#3A1A6E"
GOLD        = "#F5A623"
GREEN       = "#2ECC71"
RED         = "#E74C3C"
BLUE        = "#2E86C1"
GRAY        = "#7F8C8D"
BG          = "#F8F6FC"
CARD_BG     = "#FFFFFF"

st.markdown(f"""
<style>
/* ── global ── */
html, body, [class*="css"] {{
    font-family: 'Inter', 'Segoe UI', sans-serif;
}}
.stApp {{
    background: {BG};
}}

/* ── sidebar ── */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {PURPLE_DARK} 0%, {PURPLE} 100%);
}}
[data-testid="stSidebar"] * {{
    color: #FFFFFF !important;
}}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stDateInput label,
[data-testid="stSidebar"] .stMultiSelect label {{
    color: #E0D4F7 !important;
    font-weight: 600;
    font-size: 13px;
}}
[data-testid="stSidebar"] [data-baseweb="select"] div,
[data-testid="stSidebar"] [data-baseweb="input"] input {{
    background: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    color: #fff !important;
    border-radius: 8px !important;
}}
[data-testid="stSidebar"] [data-baseweb="tag"] {{
    background: {PURPLE_LIGHT} !important;
}}

/* ── header ── */
.dash-header {{
    background: linear-gradient(135deg, {PURPLE_DARK} 0%, {PURPLE} 60%, {PURPLE_LIGHT} 100%);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 20px rgba(91,45,142,0.25);
}}
.dash-title {{
    color: #fff;
    font-size: 26px;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.5px;
}}
.dash-subtitle {{
    color: rgba(255,255,255,0.75);
    font-size: 13px;
    margin: 4px 0 0;
}}
.dash-ts {{
    color: rgba(255,255,255,0.65);
    font-size: 12px;
    text-align: right;
}}

/* ── KPI cards ── */
.kpi-card {{
    background: {CARD_BG};
    border-radius: 14px;
    padding: 22px 24px;
    border-left: 5px solid {PURPLE};
    box-shadow: 0 2px 12px rgba(91,45,142,0.10);
    height: 130px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}}
.kpi-label {{
    font-size: 12px;
    font-weight: 600;
    color: {GRAY};
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
}}
.kpi-value {{
    font-size: 28px;
    font-weight: 800;
    color: {PURPLE_DARK};
    line-height: 1;
}}
.kpi-delta-up {{
    font-size: 12px;
    font-weight: 600;
    color: {GREEN};
}}
.kpi-delta-down {{
    font-size: 12px;
    font-weight: 600;
    color: {RED};
}}
.kpi-delta-neutral {{
    font-size: 12px;
    font-weight: 600;
    color: {GRAY};
}}

/* ── section titles ── */
.section-title {{
    font-size: 15px;
    font-weight: 700;
    color: {PURPLE_DARK};
    margin: 8px 0 14px;
    padding-left: 10px;
    border-left: 4px solid {PURPLE};
    line-height: 1.2;
}}

/* ── chart card ── */
.chart-card {{
    background: {CARD_BG};
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(91,45,142,0.08);
    margin-bottom: 18px;
}}

/* ── export button ── */
.stDownloadButton > button {{
    background: linear-gradient(135deg, {PURPLE}, {PURPLE_LIGHT}) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    width: 100% !important;
    box-shadow: 0 2px 8px rgba(91,45,142,0.3) !important;
    transition: all 0.2s !important;
}}
.stDownloadButton > button:hover {{
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}}

/* ── sidebar logo area ── */
.sidebar-logo {{
    text-align: center;
    padding: 20px 0 24px;
    border-bottom: 1px solid rgba(255,255,255,0.15);
    margin-bottom: 20px;
}}
.sidebar-logo-text {{
    font-size: 22px;
    font-weight: 900;
    color: #fff;
    letter-spacing: -0.5px;
}}
.sidebar-logo-sub {{
    font-size: 11px;
    color: rgba(255,255,255,0.6);
    letter-spacing: 1px;
    text-transform: uppercase;
}}

/* ── filter section label ── */
.filter-section {{
    font-size: 11px;
    font-weight: 700;
    color: rgba(255,255,255,0.5);
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin: 18px 0 8px;
}}

/* ── empty state ── */
.empty-state {{
    text-align: center;
    padding: 40px;
    color: {GRAY};
    font-size: 14px;
}}

/* ── overdue table ── */
.stDataFrame {{
    border-radius: 10px !important;
    overflow: hidden !important;
}}

/* ── divider ── */
.row-divider {{
    height: 1px;
    background: linear-gradient(90deg, {PURPLE_PALE}, transparent);
    margin: 8px 0 20px;
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
DATA_FILE = "YoungXCode_BusinessDataset.xlsx"
FALLBACK  = "/mnt/user-data/uploads/1781005645430_YoungXCode_BusinessDataset__4_.xlsx"

@st.cache_data(show_spinner=False)
def load_data(path):
    clients  = pd.read_excel(path, sheet_name="Clients")
    projects = pd.read_excel(path, sheet_name="Projects")
    tasks    = pd.read_excel(path, sheet_name="Tasks")
    invoices = pd.read_excel(path, sheet_name="Invoices")

    for d in [clients, projects, tasks, invoices]:
        d.columns = d.columns.str.strip()

    # Clients
    clients["Join Date"] = pd.to_datetime(clients["Join Date"], dayfirst=True, errors="coerce")

    # Projects
    projects["Start Date"]      = pd.to_datetime(projects["Start Date"],      errors="coerce")
    projects["Deadline"]        = pd.to_datetime(projects["Deadline"],        errors="coerce")
    projects["Actual End Date"] = pd.to_datetime(projects["Actual End Date"], errors="coerce")
    projects["Budget (INR)"]    = pd.to_numeric(projects["Budget (INR)"],     errors="coerce")
    projects["Amount Spent (INR)"] = pd.to_numeric(projects["Amount Spent (INR)"], errors="coerce")

    # Tasks
    tasks["Created Date"]   = pd.to_datetime(tasks["Created Date"],   errors="coerce")
    tasks["Completed Date"] = pd.to_datetime(tasks["Completed Date"], errors="coerce")
    tasks["Actual Hours"]   = pd.to_numeric(tasks["Actual Hours"],    errors="coerce")
    tasks["Estimated Hours"]= pd.to_numeric(tasks["Estimated Hours"], errors="coerce")
    tasks["month"]          = tasks["Created Date"].dt.to_period("M")

    # Invoices
    invoices["Due Date"]             = pd.to_datetime(invoices["Due Date"],  errors="coerce")
    invoices["Paid Date"]            = pd.to_datetime(invoices["Paid Date"], errors="coerce")
    invoices["Invoice Amount (INR)"] = pd.to_numeric(invoices["Invoice Amount (INR)"], errors="coerce")
    invoices["GST (INR)"]            = pd.to_numeric(invoices["GST (INR)"],            errors="coerce")

    # Synthetic monthly revenue from projects (start date month bucketing)
    projects["Revenue Month"] = projects["Start Date"].dt.to_period("M")

    return clients, projects, tasks, invoices


def resolve_file():
    if os.path.exists(DATA_FILE):
        return DATA_FILE
    if os.path.exists(FALLBACK):
        return FALLBACK
    return None


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class='sidebar-logo'>
        <div class='sidebar-logo-text'>⚡ YoungXCode</div>
        <div class='sidebar-logo-sub'>Management Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='filter-section'>📅 Date Range</div>", unsafe_allow_html=True)
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        date_start = st.date_input("From", value=datetime(2023, 1, 1), label_visibility="collapsed")
    with col_d2:
        date_end   = st.date_input("To",   value=datetime(2025, 1, 15), label_visibility="collapsed")

    st.markdown(f"<small style='color:rgba(255,255,255,0.55)'>{date_start.strftime('%d %b %Y')} → {date_end.strftime('%d %b %Y')}</small>", unsafe_allow_html=True)

    path = resolve_file()
    if path:
        with st.spinner("Loading data…"):
            clients, projects, tasks, invoices = load_data(path)

        all_clients = sorted(clients["Client Name"].dropna().unique().tolist())
        all_members = sorted(tasks["Assignee"].dropna().unique().tolist())
        all_statuses= sorted(projects["Project Status"].dropna().unique().tolist())

        st.markdown("<div class='filter-section'>🏢 Clients</div>", unsafe_allow_html=True)
        sel_clients = st.multiselect("Clients", all_clients, placeholder="All clients",
                                     label_visibility="collapsed")

        st.markdown("<div class='filter-section'>👤 Team Member</div>", unsafe_allow_html=True)
        sel_members = st.multiselect("Members", all_members, placeholder="All members",
                                     label_visibility="collapsed")

        st.markdown("<div class='filter-section'>📋 Project Status</div>", unsafe_allow_html=True)
        sel_statuses= st.multiselect("Statuses", all_statuses, placeholder="All statuses",
                                     label_visibility="collapsed")

        st.markdown("---")
        st.markdown(f"<div style='color:rgba(255,255,255,0.5);font-size:11px;text-align:center'>"
                    f"📊 {len(clients)} Clients · {len(projects)} Projects<br>{len(tasks)} Tasks · {len(invoices)} Invoices</div>",
                    unsafe_allow_html=True)
    else:
        st.error("Data file not found.")
        st.stop()


# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
TODAY = pd.Timestamp("2025-01-15")
ts    = pd.Timestamp(date_start)
te    = pd.Timestamp(date_end)

# Projects filter
filt_proj = projects.copy()
filt_proj = filt_proj[filt_proj["Start Date"].between(ts, te, inclusive="both") |
                       filt_proj["Start Date"].isna()]
if sel_clients:
    filt_proj = filt_proj[filt_proj["Client Name"].isin(sel_clients)]
if sel_statuses:
    filt_proj = filt_proj[filt_proj["Project Status"].isin(sel_statuses)]

# Tasks filter
filt_tasks = tasks.copy()
filt_tasks = filt_tasks[filt_tasks["Created Date"].between(ts, te, inclusive="both") |
                         filt_tasks["Created Date"].isna()]
if sel_members:
    filt_tasks = filt_tasks[filt_tasks["Assignee"].isin(sel_members)]
if sel_clients:
    pass  # tasks don't have client column directly

# Invoices filter
filt_inv = invoices.copy()
filt_inv = filt_inv[filt_inv["Due Date"].between(ts, te, inclusive="both") |
                     filt_inv["Due Date"].isna()]
if sel_clients:
    filt_inv = filt_inv[filt_inv["Client Name"].isin(sel_clients)]


# ─────────────────────────────────────────────
# COMPUTED METRICS
# ─────────────────────────────────────────────
def compute_kpis(filt_proj, filt_tasks, filt_inv, all_proj, all_tasks, all_inv):
    # Monthly revenue = sum of budgets in current period
    curr_rev  = filt_proj["Budget (INR)"].sum()
    # Prev period: same length before ts
    period_days = max((te - ts).days, 1)
    prev_ts   = ts - timedelta(days=period_days)
    prev_proj = all_proj[all_proj["Start Date"].between(prev_ts, ts)]
    if sel_clients:
        prev_proj = prev_proj[prev_proj["Client Name"].isin(sel_clients)]
    prev_rev  = prev_proj["Budget (INR)"].sum()
    rev_delta = curr_rev - prev_rev

    # Active projects
    active_now  = (filt_proj["Project Status"].isin(["In Progress","Delayed","On Hold"])).sum()
    active_prev = (prev_proj["Project Status"].isin(["In Progress","Delayed","On Hold"])).sum()
    active_delta= int(active_now) - int(active_prev)

    # Invoice collection rate
    paid      = filt_inv[filt_inv["Payment Status"] == "Paid"]["Invoice Amount (INR)"].sum()
    total_inv = filt_inv["Invoice Amount (INR)"].sum()
    coll_rate = (paid / total_inv * 100) if total_inv > 0 else 0
    prev_inv  = all_inv[all_inv["Due Date"].between(prev_ts, ts)]
    if sel_clients:
        prev_inv = prev_inv[prev_inv["Client Name"].isin(sel_clients)]
    paid_prev      = prev_inv[prev_inv["Payment Status"] == "Paid"]["Invoice Amount (INR)"].sum()
    total_inv_prev = prev_inv["Invoice Amount (INR)"].sum()
    coll_prev = (paid_prev / total_inv_prev * 100) if total_inv_prev > 0 else 0
    coll_delta= coll_rate - coll_prev

    # Team utilization
    avail_hrs  = filt_tasks["Assignee"].nunique() * 160
    actual_hrs = filt_tasks["Actual Hours"].dropna().sum()
    util_rate  = (actual_hrs / avail_hrs * 100) if avail_hrs > 0 else 0
    prev_tasks = all_tasks[all_tasks["Created Date"].between(prev_ts, ts)]
    if sel_members:
        prev_tasks = prev_tasks[prev_tasks["Assignee"].isin(sel_members)]
    avail_prev  = prev_tasks["Assignee"].nunique() * 160
    actual_prev = prev_tasks["Actual Hours"].dropna().sum()
    util_prev   = (actual_prev / avail_prev * 100) if avail_prev > 0 else 0
    util_delta  = util_rate - util_prev

    return (curr_rev, rev_delta, active_now, active_delta,
            coll_rate, coll_delta, util_rate, util_delta)

(curr_rev, rev_delta, active_now, active_delta,
 coll_rate, coll_delta, util_rate, util_delta) = compute_kpis(
     filt_proj, filt_tasks, filt_inv, projects, tasks, invoices)


# ─────────────────────────────────────────────
# HELPER: KPI CARD HTML
# ─────────────────────────────────────────────
def kpi_card(label, value, delta, fmt="number", icon="📊"):
    if fmt == "currency":
        val_str = f"₹{value/1e6:.2f}M" if value >= 1e6 else f"₹{value:,.0f}"
        dlt_str = f"₹{abs(delta)/1e6:.2f}M" if abs(delta) >= 1e6 else f"₹{abs(delta):,.0f}"
    elif fmt == "percent":
        val_str = f"{value:.1f}%"
        dlt_str = f"{abs(delta):.1f}%"
    else:
        val_str = f"{int(value):,}"
        dlt_str = f"{int(abs(delta))}"

    if delta > 0:
        dlt_html = f"<div class='kpi-delta-up'>▲ {dlt_str} vs prev period</div>"
    elif delta < 0:
        dlt_html = f"<div class='kpi-delta-down'>▼ {dlt_str} vs prev period</div>"
    else:
        dlt_html = f"<div class='kpi-delta-neutral'>— No change</div>"

    return f"""
    <div class='kpi-card'>
        <div class='kpi-label'>{icon} {label}</div>
        <div class='kpi-value'>{val_str}</div>
        {dlt_html}
    </div>
    """


# ─────────────────────────────────────────────
# CHART HELPERS
# ─────────────────────────────────────────────
CHART_CONFIG = {"displayModeBar": False}

def style_fig(fig, height=340):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", size=12, color="#444"),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5,
                    font=dict(size=11)),
    )
    fig.update_xaxes(showgrid=False, tickfont=dict(size=11))
    fig.update_yaxes(gridcolor="#F0EBF8", gridwidth=1, tickfont=dict(size=11))
    return fig


def revenue_trend_chart(filt_proj):
    if filt_proj.empty:
        return None
    monthly = (filt_proj.groupby("Revenue Month")["Budget (INR)"]
               .sum().reset_index())
    monthly["Month"] = monthly["Revenue Month"].dt.strftime("%b %Y")
    monthly = monthly.sort_values("Revenue Month")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly["Month"],
        y=monthly["Budget (INR)"] / 1e6,
        name="Revenue",
        marker=dict(
            color=monthly["Budget (INR)"],
            colorscale=[[0, PURPLE_PALE], [0.5, PURPLE_LIGHT], [1, PURPLE_DARK]],
            line=dict(width=0),
        ),
        hovertemplate="<b>%{x}</b><br>₹%{y:.2f}M<extra></extra>",
    ))
    # Trend line
    if len(monthly) > 1:
        z = np.polyfit(range(len(monthly)), monthly["Budget (INR)"].values / 1e6, 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=monthly["Month"],
            y=[p(i) for i in range(len(monthly))],
            mode="lines",
            name="Trend",
            line=dict(color=GOLD, width=2, dash="dot"),
            hoverinfo="skip",
        ))
    fig.update_layout(title=dict(text="Monthly Revenue (₹M)", font=dict(size=14, color=PURPLE_DARK)))
    fig.update_yaxes(tickprefix="₹", ticksuffix="M")
    return style_fig(fig)


def project_status_chart(filt_proj):
    if filt_proj.empty:
        return None
    status_counts = filt_proj["Project Status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]

    STATUS_COLORS = {
        "Completed":   "#2ECC71",
        "In Progress": PURPLE,
        "On Hold":     GOLD,
        "Delayed":     RED,
        "Cancelled":   GRAY,
    }
    colors = [STATUS_COLORS.get(s, BLUE) for s in status_counts["Status"]]

    fig = go.Figure(go.Pie(
        labels=status_counts["Status"],
        values=status_counts["Count"],
        hole=0.52,
        marker=dict(colors=colors, line=dict(color="white", width=2.5)),
        textinfo="label+percent",
        textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>%{value} projects (%{percent})<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Project Status Distribution", font=dict(size=14, color=PURPLE_DARK)),
        annotations=[dict(text=f"<b>{len(filt_proj)}</b><br>Projects",
                          x=0.5, y=0.5, font_size=14, showarrow=False,
                          font=dict(color=PURPLE_DARK))],
    )
    return style_fig(fig, height=340)


def team_workload_chart(filt_tasks):
    if filt_tasks.empty:
        return None
    workload = (filt_tasks.groupby("Assignee")
                .agg(assigned=("Project Name","count"),
                     completed=("Completed Date", lambda x: x.notna().sum()),
                     actual_hrs=("Actual Hours", "sum"))
                .reset_index()
                .sort_values("assigned", ascending=True))

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=workload["Assignee"],
        x=workload["assigned"],
        name="Assigned",
        orientation="h",
        marker=dict(color=PURPLE, opacity=0.85),
        hovertemplate="<b>%{y}</b><br>Assigned: %{x}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=workload["Assignee"],
        x=workload["completed"],
        name="Completed",
        orientation="h",
        marker=dict(color=GREEN, opacity=0.85),
        hovertemplate="<b>%{y}</b><br>Completed: %{x}<extra></extra>",
    ))
    fig.update_layout(
        barmode="overlay",
        title=dict(text="Team Workload — Assigned vs Completed Tasks",
                   font=dict(size=14, color=PURPLE_DARK)),
        xaxis_title="Tasks",
    )
    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=False)
    return style_fig(fig, height=400)


def overdue_table(filt_inv):
    if filt_inv.empty:
        return pd.DataFrame()
    overdue = filt_inv[filt_inv["Payment Status"].isin(["Unpaid","Partially Paid","Overdue"])].copy()
    overdue["Overdue Days"] = (TODAY - overdue["Due Date"]).dt.days.clip(lower=0)
    overdue = overdue[overdue["Overdue Days"] > 0].sort_values("Overdue Days", ascending=False)

    if overdue.empty:
        return pd.DataFrame()

    display = overdue[["Client Name","Invoice Amount (INR)","Due Date",
                        "Overdue Days","Payment Status"]].copy()
    display["Invoice Amount (INR)"] = display["Invoice Amount (INR)"].apply(lambda x: f"₹{x:,.0f}")
    display["Due Date"] = display["Due Date"].dt.strftime("%d %b %Y")
    display.index = range(1, len(display)+1)
    display.columns = ["Client","Amount","Due Date","Overdue Days","Status"]
    return display


# ─────────────────────────────────────────────
# EXPORT DATA
# ─────────────────────────────────────────────
def build_export():
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        filt_proj.to_excel(writer, sheet_name="Projects",  index=False)
        filt_tasks.to_excel(writer, sheet_name="Tasks",    index=False)
        filt_inv.to_excel(writer,   sheet_name="Invoices", index=False)
    return buf.getvalue()


# ─────────────────────────────────────────────
# MAIN LAYOUT
# ─────────────────────────────────────────────

# ── Header ──
st.markdown(f"""
<div class='dash-header'>
    <div>
        <div class='dash-title'>⚡ YoungXCode Management Dashboard</div>
        <div class='dash-subtitle'>Executive · Financial · Operational · Project Intelligence</div>
    </div>
    <div class='dash-ts'>
        🕐 Last updated<br><b>{TODAY.strftime('%d %b %Y')}</b><br>
        <small>{len(filt_proj)} projects · {len(filt_tasks)} tasks · {len(filt_inv)} invoices</small>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────── ROW 1 — KPI CARDS ───────────
st.markdown("<div class='section-title'>📌 Key Performance Indicators</div>", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(kpi_card("Monthly Revenue",          curr_rev,   rev_delta,    "currency", "💰"), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_card("Active Projects",           active_now, active_delta, "number",   "📁"), unsafe_allow_html=True)
with k3:
    st.markdown(kpi_card("Invoice Collection Rate",  coll_rate,  coll_delta,   "percent",  "🧾"), unsafe_allow_html=True)
with k4:
    st.markdown(kpi_card("Team Utilization",          util_rate,  util_delta,   "percent",  "👥"), unsafe_allow_html=True)

st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

# ─────────── ROW 2 — CHARTS ───────────
st.markdown("<div class='section-title'>📈 Revenue & Project Insights</div>", unsafe_allow_html=True)

r2c1, r2c2 = st.columns([3, 2])

with r2c1:
    with st.container():
        rev_fig = revenue_trend_chart(filt_proj)
        if rev_fig:
            st.plotly_chart(rev_fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.markdown("<div class='empty-state'>📊 No revenue data for selected filters.</div>",
                        unsafe_allow_html=True)

with r2c2:
    with st.container():
        pie_fig = project_status_chart(filt_proj)
        if pie_fig:
            st.plotly_chart(pie_fig, use_container_width=True, config=CHART_CONFIG)
        else:
            st.markdown("<div class='empty-state'>🗂 No project data for selected filters.</div>",
                        unsafe_allow_html=True)

st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

# ─────────── ROW 3 — WORKLOAD + OVERDUE ───────────
st.markdown("<div class='section-title'>👥 Team Workload & Invoice Alerts</div>", unsafe_allow_html=True)

r3c1, r3c2 = st.columns([3, 2])

with r3c1:
    wl_fig = team_workload_chart(filt_tasks)
    if wl_fig:
        st.plotly_chart(wl_fig, use_container_width=True, config=CHART_CONFIG)
    else:
        st.markdown("<div class='empty-state'>👤 No task data for selected filters.</div>",
                    unsafe_allow_html=True)

with r3c2:
    st.markdown("<div style='font-size:14px;font-weight:700;color:#5B2D8E;margin-bottom:10px'>"
                "🔴 Overdue Invoices</div>", unsafe_allow_html=True)

    od_table = overdue_table(filt_inv)
    if not od_table.empty:
        # Color-code status column
        def highlight_status(val):
            if val == "Unpaid":
                return "background-color:#FDEDEC;color:#C0392B;font-weight:600"
            if val == "Partially Paid":
                return "background-color:#FEF9E7;color:#B7770D;font-weight:600"
            return ""

        styled = od_table.style.applymap(highlight_status, subset=["Status"])
        st.dataframe(styled, use_container_width=True, height=360)
        st.markdown(f"<small style='color:{RED};font-weight:600'>"
                    f"⚠ {len(od_table)} overdue invoices detected</small>",
                    unsafe_allow_html=True)
    else:
        st.markdown("<div class='empty-state'>✅ No overdue invoices in selected range.</div>",
                    unsafe_allow_html=True)

st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

# ─────────── EXPORT BUTTON ───────────
st.markdown("<div class='section-title'>📥 Export Filtered Data</div>", unsafe_allow_html=True)
exp_c1, exp_c2, exp_c3 = st.columns([1, 1, 2])

with exp_c1:
    export_bytes = build_export()
    st.download_button(
        label="⬇ Download Excel Report",
        data=export_bytes,
        file_name=f"YoungXCode_Dashboard_{date_start}_{date_end}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

with exp_c2:
    csv_data = filt_proj.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Download Projects CSV",
        data=csv_data,
        file_name=f"YoungXCode_Projects_{date_start}_{date_end}.csv",
        mime="text/csv",
    )

# ─────────── FOOTER ───────────
st.markdown(f"""
<div style='text-align:center;padding:28px 0 10px;color:{GRAY};font-size:12px;border-top:1px solid {PURPLE_PALE};margin-top:20px'>
    <b style='color:{PURPLE}'>⚡ YoungXCode</b> · Management Dashboard ·
    Built with Streamlit & Plotly ·
    Data as of {TODAY.strftime('%d %b %Y')}
</div>
""", unsafe_allow_html=True)
