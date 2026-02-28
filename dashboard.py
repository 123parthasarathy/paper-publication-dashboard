import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import re
from datetime import datetime

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Research Publication Tracker",
    page_icon="https://em-content.zobj.net/source/twitter/408/crown_1f451.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# ROYAL PURPLE PALETTE
# ============================================================
# Primary purples
ROYAL_DEEP = "#2D1B69"
ROYAL_PRIMARY = "#5B2C8E"
ROYAL_VIBRANT = "#7C3AED"
ROYAL_MEDIUM = "#8B5CF6"
ROYAL_LIGHT = "#A78BFA"
ROYAL_SOFT = "#C4B5FD"
ROYAL_FAINT = "#EDE9FE"
ROYAL_WASH = "#F5F3FF"

# Accent colors (complementary to purple)
GOLD = "#F59E0B"
GOLD_LIGHT = "#FCD34D"
GOLD_DARK = "#D97706"
EMERALD = "#10B981"
EMERALD_DARK = "#059669"
ROSE = "#F43F5E"
ROSE_LIGHT = "#FB7185"
SKY = "#0EA5E9"
SKY_LIGHT = "#38BDF8"
AMBER = "#F59E0B"
TEAL = "#14B8A6"
INDIGO = "#6366F1"
FUCHSIA = "#D946EF"
SLATE = "#64748B"

# Status-specific colors (purple-themed)
STATUS_COLORS = {
    "Published": EMERALD,
    "Accepted": ROYAL_VIBRANT,
    "Communicated to Riya": GOLD,
    "Under Review": SKY,
    "Rejected": ROSE,
    "In Progress": TEAL,
    "Other": SLATE,
}

CHART_FONT = dict(family="'Inter', 'Segoe UI', system-ui, sans-serif", size=12, color="#4A3768")
TITLE_FONT = dict(family="'Inter', 'Segoe UI', system-ui, sans-serif", size=17, color=ROYAL_DEEP)
CHART_BG = "rgba(0,0,0,0)"
PLOT_BG = "rgba(245,243,255,0.4)"
GRID_COLOR = "rgba(139,92,246,0.08)"

# ============================================================
# CUSTOM CSS - ROYAL PURPLE THEME
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ---- Global ---- */
    .stApp { background: linear-gradient(170deg, #0F0A1A 0%, #1A1035 25%, #1E1245 50%, #160D30 100%); }
    .stApp, .stApp * { font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important; }

    /* ---- Header ---- */
    .royal-header {
        text-align: center; padding: 1.2rem 0 0.3rem;
        background: linear-gradient(135deg, #7C3AED, #A78BFA, #F59E0B, #A78BFA, #7C3AED);
        background-size: 300% 300%;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 2.6rem; font-weight: 800; letter-spacing: -0.02em;
        animation: shimmer 6s ease infinite;
    }
    @keyframes shimmer { 0%,100%{background-position:0% 50%} 50%{background-position:100% 50%} }
    .royal-sub {
        text-align: center; color: #A78BFA; font-size: 0.95rem; font-weight: 400;
        letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 1.2rem;
    }

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A1035 0%, #2D1B69 50%, #1A1035 100%) !important;
    }
    section[data-testid="stSidebar"] * { color: #E8E0F5 !important; }
    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] .stMultiSelect > div > div,
    section[data-testid="stSidebar"] .stTextInput > div > div > input {
        background: rgba(124,58,237,0.15) !important;
        border-color: rgba(167,139,250,0.3) !important;
        color: #E8E0F5 !important;
    }
    section[data-testid="stSidebar"] hr { border-color: rgba(167,139,250,0.2) !important; }

    /* ---- Metric cards ---- */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(124,58,237,0.15) 0%, rgba(99,102,241,0.10) 100%);
        border: 1px solid rgba(167,139,250,0.25);
        border-radius: 14px; padding: 14px 16px;
        box-shadow: 0 4px 20px rgba(91,44,142,0.15);
        backdrop-filter: blur(10px);
    }
    div[data-testid="stMetric"] label { color: #C4B5FD !important; font-weight: 500 !important; font-size: 0.78rem !important; text-transform: uppercase; letter-spacing: 0.05em; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #F5F3FF !important; font-weight: 700 !important; }

    /* ---- KPI Cards ---- */
    .kpi-row { display: flex; gap: 12px; margin-bottom: 0.8rem; flex-wrap: wrap; }
    .kpi-card {
        flex: 1; min-width: 140px; padding: 16px 14px; border-radius: 16px; text-align: center;
        backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 12px 40px rgba(91,44,142,0.3); }
    .kpi-icon { font-size: 1.5rem; margin-bottom: 4px; }
    .kpi-val { font-size: 2rem; font-weight: 800; line-height: 1.1; }
    .kpi-label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; opacity: 0.85; margin-top: 4px; font-weight: 500; }
    .kpi-sub { font-size: 0.68rem; opacity: 0.6; margin-top: 2px; }

    .kpi-purple { background: linear-gradient(135deg, #5B2C8E, #7C3AED); color: #F5F3FF; }
    .kpi-emerald { background: linear-gradient(135deg, #059669, #10B981); color: #F0FDF4; }
    .kpi-violet { background: linear-gradient(135deg, #6D28D9, #8B5CF6); color: #F5F3FF; }
    .kpi-gold { background: linear-gradient(135deg, #D97706, #F59E0B); color: #1A1035; }
    .kpi-sky { background: linear-gradient(135deg, #0369A1, #0EA5E9); color: #F0F9FF; }
    .kpi-rose { background: linear-gradient(135deg, #BE123C, #F43F5E); color: #FFF1F2; }

    /* ---- Section headers ---- */
    .section-header {
        display: flex; align-items: center; gap: 10px;
        padding: 10px 0 6px; margin-top: 0.8rem;
        border-bottom: 2px solid rgba(124,58,237,0.3);
    }
    .section-header .icon { font-size: 1.2rem; }
    .section-header .text { font-size: 1.1rem; font-weight: 700; color: #C4B5FD; letter-spacing: -0.01em; }
    .section-header .badge {
        font-size: 0.65rem; background: rgba(124,58,237,0.3); color: #A78BFA;
        padding: 2px 8px; border-radius: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;
    }

    /* ---- Glass panels ---- */
    .glass-panel {
        background: linear-gradient(135deg, rgba(30,18,69,0.8) 0%, rgba(45,27,105,0.6) 100%);
        border: 1px solid rgba(167,139,250,0.15);
        border-radius: 16px; padding: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        backdrop-filter: blur(16px);
    }

    /* ---- Pricing cards ---- */
    .price-card {
        border-radius: 16px; padding: 20px; position: relative; overflow: hidden;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .price-card::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
    }
    .price-sci { background: linear-gradient(135deg, rgba(124,58,237,0.25), rgba(99,102,241,0.15)); }
    .price-sci::before { background: linear-gradient(90deg, #7C3AED, #A78BFA); }
    .price-scopus { background: linear-gradient(135deg, rgba(245,158,11,0.2), rgba(217,119,6,0.1)); }
    .price-scopus::before { background: linear-gradient(90deg, #F59E0B, #FCD34D); }
    .price-title { font-size: 1rem; font-weight: 700; margin-bottom: 8px; }
    .price-total { font-size: 1.6rem; font-weight: 800; margin-bottom: 10px; }
    .price-step { font-size: 0.82rem; padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,0.06); display: flex; justify-content: space-between; }
    .price-step:last-child { border-bottom: none; }

    /* ---- Paper list ---- */
    .paper-item {
        background: rgba(124,58,237,0.08); border: 1px solid rgba(167,139,250,0.12);
        border-radius: 12px; padding: 12px 16px; margin-bottom: 8px;
        transition: border-color 0.2s;
    }
    .paper-item:hover { border-color: rgba(167,139,250,0.35); }
    .paper-title-text { font-size: 0.85rem; font-weight: 600; color: #E8E0F5; line-height: 1.4; }
    .paper-meta { font-size: 0.72rem; color: #A78BFA; margin-top: 4px; }
    .status-badge {
        display: inline-block; font-size: 0.65rem; font-weight: 600; padding: 2px 10px;
        border-radius: 10px; text-transform: uppercase; letter-spacing: 0.04em;
    }
    .status-published { background: rgba(16,185,129,0.2); color: #6EE7B7; }
    .status-accepted { background: rgba(124,58,237,0.25); color: #C4B5FD; }
    .status-communicated { background: rgba(245,158,11,0.2); color: #FCD34D; }
    .status-review { background: rgba(14,165,233,0.2); color: #7DD3FC; }

    /* ---- Misc ---- */
    h1, h2, h3 { color: #C4B5FD !important; }
    .stMarkdown p, .stMarkdown li { color: #D4CCEC; }
    .stDataFrame { border-radius: 12px; overflow: hidden; }
    div[data-testid="stDataFrame"] > div { border-radius: 12px; }

    /* ---- Client cards ---- */
    .client-grid { display: flex; flex-wrap: wrap; gap: 8px; }
    .client-chip {
        background: rgba(124,58,237,0.15); border: 1px solid rgba(167,139,250,0.2);
        border-radius: 20px; padding: 6px 14px; font-size: 0.8rem; color: #C4B5FD; font-weight: 500;
    }

    .divider { border: none; border-top: 1px solid rgba(167,139,250,0.15); margin: 0.8rem 0; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# CHART LAYOUT
# ============================================================
def royal_layout(**kwargs):
    layout = dict(
        template="plotly_dark",
        font=CHART_FONT,
        title_font=TITLE_FONT,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(30,18,69,0.4)",
        margin=dict(l=50, r=30, t=80, b=50),
        xaxis=dict(gridcolor=GRID_COLOR, showgrid=True, zeroline=False,
                   tickfont=dict(color="#A78BFA", size=11)),
        yaxis=dict(gridcolor=GRID_COLOR, showgrid=True, zeroline=False,
                   tickfont=dict(color="#A78BFA", size=11)),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.04,
            xanchor="center", x=0.5, font=dict(size=10, color="#C4B5FD"),
            bgcolor="rgba(0,0,0,0)",
        ),
        title=dict(y=0.96, font=dict(color="#E8E0F5", size=15)),
    )
    layout.update(kwargs)
    return layout


# ============================================================
# DATA LOADING (unchanged logic, optimized)
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def safe_float(val):
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace(",", "").replace("Nill", "0").replace("nill", "0").replace("NIL", "0").replace("-", "0")
    try:
        return float(s)
    except ValueError:
        return 0.0


def parse_paper_sheet(filepath, sheet_name):
    df = pd.read_excel(filepath, sheet_name=sheet_name, header=None)
    papers = []
    for i in range(3, len(df)):
        row = df.iloc[i]
        sno = row.iloc[1]
        if pd.isna(sno):
            continue
        try:
            sno_int = int(float(sno))
        except (ValueError, TypeError):
            continue

        authors = []
        for name_col, amt_col, email_col in [(3,4,5),(6,7,8),(9,10,11),(12,13,14),(15,16,17)]:
            name = str(row.iloc[name_col]).strip() if pd.notna(row.iloc[name_col]) else ""
            amt = safe_float(row.iloc[amt_col])
            email = str(row.iloc[email_col]).strip() if pd.notna(row.iloc[email_col]) else ""
            if name and name.lower() not in ("", "nan", "not available", "-", "can add", "can add authors"):
                authors.append({"name": name, "amount": amt, "email": email})

        status_raw = str(row.iloc[26]).strip() if len(row) > 26 and pd.notna(row.iloc[26]) else ""
        if "published" in status_raw.lower():
            status = "Published"
        elif "accepted" in status_raw.lower():
            status = "Accepted"
        elif "communicated" in status_raw.lower():
            status = "Communicated to Riya"
        elif "review" in status_raw.lower():
            status = "Under Review"
        elif "rejected" in status_raw.lower():
            status = "Rejected"
        elif status_raw:
            status = status_raw
        else:
            status = "In Progress"

        papers.append({
            "SNo": sno_int,
            "Title": str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else "",
            "Authors": authors,
            "Author_Names": ", ".join([a["name"] for a in authors]),
            "Num_Authors": len(authors),
            "Total_Amount": safe_float(row.iloc[18]),
            "Payment_1": safe_float(row.iloc[19]),
            "Payment_2": safe_float(row.iloc[20]),
            "Payment_3": safe_float(row.iloc[21]),
            "Payment_4": safe_float(row.iloc[22]),
            "Payment_5": safe_float(row.iloc[23]),
            "Total_Paid": safe_float(row.iloc[24]),
            "Balance": safe_float(row.iloc[25]),
            "Status": status,
            "Status_Raw": status_raw,
            "Source": sheet_name.strip(),
        })
    return papers


@st.cache_data
def load_data():
    filepath = os.path.join(BASE_DIR, "Paper-Publishing-Work-In-Progress.xlsx")
    if not os.path.exists(filepath):
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    xl = pd.ExcelFile(filepath)
    all_papers = []
    for sheet in xl.sheet_names:
        if "work" in sheet.lower().strip():
            all_papers.extend(parse_paper_sheet(filepath, sheet))

    df_papers = pd.DataFrame(all_papers) if all_papers else pd.DataFrame()

    df_clients = pd.DataFrame()
    if "clients details" in xl.sheet_names:
        df_clients = pd.read_excel(filepath, sheet_name="clients details")

    df_info = pd.DataFrame()
    for sheet in xl.sheet_names:
        if "info" in sheet.lower():
            df_info = pd.read_excel(filepath, sheet_name=sheet, header=None)
            break

    return df_papers, df_clients, df_info


df_papers, df_clients, df_info = load_data()

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown("""
<div style='text-align:center; padding: 12px 0 8px;'>
    <div style='font-size:1.5rem;'>&#x1F451;</div>
    <div style='font-size:1rem; font-weight:700; color:#C4B5FD; letter-spacing:0.03em;'>Research Tracker</div>
    <div style='font-size:0.7rem; color:#8B7BAA; text-transform:uppercase; letter-spacing:0.1em;'>Filters & Controls</div>
</div>
""", unsafe_allow_html=True)

if not df_papers.empty:
    all_sources = sorted(df_papers["Source"].unique().tolist())
    selected_sources = st.sidebar.multiselect("Work Category", all_sources, default=all_sources)

    all_statuses = sorted(df_papers["Status"].unique().tolist())
    selected_statuses = st.sidebar.multiselect("Paper Status", all_statuses, default=all_statuses)

    author_search = st.sidebar.text_input("Search Author", "")
    title_search = st.sidebar.text_input("Search Paper Title", "")

    filtered = df_papers[
        (df_papers["Source"].isin(selected_sources))
        & (df_papers["Status"].isin(selected_statuses))
    ].copy()
    if author_search:
        filtered = filtered[filtered["Author_Names"].str.contains(author_search, case=False, na=False)]
    if title_search:
        filtered = filtered[filtered["Title"].str.contains(title_search, case=False, na=False)]
else:
    filtered = pd.DataFrame()

st.sidebar.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.sidebar.markdown(f"""
<div style='text-align:center; padding:8px 0; font-size:0.72rem; color:#8B7BAA;'>
    Last updated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}
</div>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
st.markdown('<div class="royal-header">Research Publication Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="royal-sub">Paper Publication &bull; Financial Analytics &bull; Author Insights</div>', unsafe_allow_html=True)

# ============================================================
# KPI CARDS
# ============================================================
if not df_papers.empty:
    total_papers = len(df_papers)
    published = len(df_papers[df_papers["Status"] == "Published"])
    accepted = len(df_papers[df_papers["Status"] == "Accepted"])
    communicated = len(df_papers[df_papers["Status"] == "Communicated to Riya"])
    total_paid = df_papers["Total_Paid"].sum()
    total_balance = df_papers["Balance"].sum()
    total_revenue = df_papers["Total_Amount"].sum()

    # Count unique authors
    all_auth_set = set()
    for auth_list in df_papers["Authors"]:
        for a in auth_list:
            all_auth_set.add(a["name"].lower().strip())
    unique_authors = len(all_auth_set)
else:
    total_papers = published = accepted = communicated = unique_authors = 0
    total_paid = total_balance = total_revenue = 0

st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card kpi-purple">
        <div class="kpi-icon">&#x1F4DA;</div>
        <div class="kpi-val">{total_papers}</div>
        <div class="kpi-label">Total Papers</div>
        <div class="kpi-sub">All categories</div>
    </div>
    <div class="kpi-card kpi-emerald">
        <div class="kpi-icon">&#x2705;</div>
        <div class="kpi-val">{published}</div>
        <div class="kpi-label">Published</div>
        <div class="kpi-sub">Successfully done</div>
    </div>
    <div class="kpi-card kpi-violet">
        <div class="kpi-icon">&#x1F3AF;</div>
        <div class="kpi-val">{accepted}</div>
        <div class="kpi-label">Accepted</div>
        <div class="kpi-sub">Awaiting publish</div>
    </div>
    <div class="kpi-card kpi-gold">
        <div class="kpi-icon">&#x1F4E8;</div>
        <div class="kpi-val">{communicated}</div>
        <div class="kpi-label">Communicated</div>
        <div class="kpi-sub">Sent to Riya</div>
    </div>
    <div class="kpi-card kpi-sky">
        <div class="kpi-icon">&#x1F465;</div>
        <div class="kpi-val">{unique_authors}</div>
        <div class="kpi-label">Authors</div>
        <div class="kpi-sub">Unique researchers</div>
    </div>
    <div class="kpi-card kpi-rose">
        <div class="kpi-icon">&#x1F4B0;</div>
        <div class="kpi-val">&#x20B9;{total_balance/1000:.0f}K</div>
        <div class="kpi-label">Balance Due</div>
        <div class="kpi-sub">INR pending</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# METRICS ROW
# ============================================================
if not filtered.empty:
    filt_auth_set = set()
    for auth_list in filtered["Authors"]:
        for a in auth_list:
            filt_auth_set.add(a["name"].lower().strip())

    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
    mc1.metric("Filtered Papers", len(filtered))
    mc2.metric("Unique Authors", len(filt_auth_set))
    mc3.metric("Avg Team Size", f"{filtered['Num_Authors'].mean():.1f}")
    mc4.metric("Total Collected", f"INR {filtered['Total_Paid'].sum():,.0f}")
    collection_rate = (filtered['Total_Paid'].sum() / max(filtered['Total_Amount'].sum(), 1)) * 100
    mc5.metric("Collection Rate", f"{collection_rate:.0f}%")

# ============================================================
# SECTION: Status Overview + Pipeline
# ============================================================
if not filtered.empty:
    st.markdown("""<div class="section-header">
        <span class="icon">&#x1F4CA;</span>
        <span class="text">Publication Status Overview</span>
        <span class="badge">Analytics</span>
    </div>""", unsafe_allow_html=True)

    r1c1, r1c2 = st.columns(2)

    with r1c1:
        status_counts = filtered["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        colors = [STATUS_COLORS.get(s, SLATE) for s in status_counts["Status"]]
        total = status_counts["Count"].sum()

        fig = go.Figure(data=[go.Pie(
            labels=status_counts["Status"], values=status_counts["Count"],
            marker=dict(colors=colors, line=dict(color=ROYAL_DEEP, width=3)),
            hole=0.55,
            text=[f"{r['Count']}" for _, r in status_counts.iterrows()],
            textinfo="text",
            textposition="inside",
            textfont=dict(size=16, color="white", family="Inter"),
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
        )])
        fig.add_annotation(text=f"<b>{total}</b><br><span style='font-size:11px;color:#A78BFA'>Total</span>",
                           x=0.5, y=0.5, font=dict(size=28, color="#E8E0F5"), showarrow=False)
        fig.update_layout(**royal_layout(
            title="Status Distribution", height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.02, xanchor="center", x=0.5,
                        font=dict(size=10, color="#C4B5FD")),
        ))
        st.plotly_chart(fig, width="stretch")

    with r1c2:
        # Funnel
        status_order = ["Communicated to Riya", "Under Review", "Accepted", "Published"]
        status_vals = [len(filtered[filtered["Status"] == s]) for s in status_order]

        fig = go.Figure(data=[go.Funnel(
            y=[s.replace("Communicated to Riya", "Communicated") for s in status_order],
            x=status_vals,
            textinfo="value+percent initial",
            textfont=dict(size=14, color="white", family="Inter"),
            marker=dict(
                color=[STATUS_COLORS.get(s, SLATE) for s in status_order],
                line=dict(width=1, color=ROYAL_DEEP),
            ),
            connector=dict(line=dict(color="rgba(167,139,250,0.3)", width=2)),
        )])
        fig.update_layout(**royal_layout(
            title="Publication Pipeline", height=400,
        ))
        st.plotly_chart(fig, width="stretch")

# ============================================================
# SECTION: Author Analysis
# ============================================================
if not filtered.empty:
    st.markdown("""<div class="section-header">
        <span class="icon">&#x1F9D1;&#x200D;&#x1F52C;</span>
        <span class="text">Author Contribution Analysis</span>
        <span class="badge">Research</span>
    </div>""", unsafe_allow_html=True)

    author_stats = {}
    for _, paper in filtered.iterrows():
        for author in paper["Authors"]:
            name = author["name"].strip()
            key = name.lower()
            if key not in author_stats:
                author_stats[key] = {"name": name, "papers": 0, "total_amount": 0, "statuses": []}
            author_stats[key]["papers"] += 1
            author_stats[key]["total_amount"] += author["amount"]
            author_stats[key]["statuses"].append(paper["Status"])

    df_authors = pd.DataFrame(author_stats.values())

    r2c1, r2c2 = st.columns(2)

    with r2c1:
        top_a = df_authors.sort_values("papers", ascending=True).tail(12)
        # Gradient purple colors
        n = len(top_a)
        grad_colors = [f"rgba(124,58,237,{0.3 + 0.7 * i / max(n - 1, 1)})" for i in range(n)]

        fig = go.Figure(data=[go.Bar(
            x=top_a["papers"], y=top_a["name"], orientation="h",
            marker=dict(color=grad_colors, line=dict(width=0), cornerradius=6),
            text=top_a["papers"], textposition="outside",
            textfont=dict(size=13, color="#C4B5FD"),
        )])
        fig.update_layout(**royal_layout(
            title="Top Authors by Paper Count", height=420,
            xaxis=dict(gridcolor=GRID_COLOR, dtick=1),
            yaxis=dict(tickfont=dict(size=11, color="#E8E0F5")),
        ))
        st.plotly_chart(fig, width="stretch")

    with r2c2:
        top_amt = df_authors[df_authors["total_amount"] > 0].sort_values("total_amount", ascending=True).tail(12)
        if not top_amt.empty:
            n2 = len(top_amt)
            gold_grad = [f"rgba(245,158,11,{0.3 + 0.7 * i / max(n2 - 1, 1)})" for i in range(n2)]
            fig = go.Figure(data=[go.Bar(
                x=top_amt["total_amount"], y=top_amt["name"], orientation="h",
                marker=dict(color=gold_grad, line=dict(width=0), cornerradius=6),
                text=[f"INR {v:,.0f}" for v in top_amt["total_amount"]], textposition="outside",
                textfont=dict(size=11, color="#FCD34D"),
            )])
            fig.update_layout(**royal_layout(
                title="Authors by Financial Contribution", height=420,
                yaxis=dict(tickfont=dict(size=11, color="#E8E0F5")),
            ))
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No financial data available for authors.")

    # Team size distribution + Source breakdown (compact row)
    r2d1, r2d2 = st.columns(2)

    with r2d1:
        auth_dist = filtered["Num_Authors"].value_counts().sort_index().reset_index()
        auth_dist.columns = ["Num", "Papers"]
        team_colors = [ROYAL_MEDIUM, ROYAL_VIBRANT, EMERALD, GOLD, ROSE, SKY]
        fig = go.Figure(data=[go.Bar(
            x=[f"{n} Author{'s' if n > 1 else ''}" for n in auth_dist["Num"]],
            y=auth_dist["Papers"],
            marker=dict(color=[team_colors[i % len(team_colors)] for i in range(len(auth_dist))],
                        line=dict(width=0), cornerradius=8),
            text=auth_dist["Papers"], textposition="outside",
            textfont=dict(size=14, color="#C4B5FD"),
            width=0.5,
        )])
        fig.update_layout(**royal_layout(
            title="Papers by Team Size", height=380,
            yaxis=dict(dtick=1, range=[0, auth_dist["Papers"].max() * 1.3]),
        ))
        st.plotly_chart(fig, width="stretch")

    with r2d2:
        source_status = filtered.groupby(["Source", "Status"]).size().reset_index(name="Count")
        fig = go.Figure()
        for status in filtered["Status"].unique():
            ss = source_status[source_status["Status"] == status]
            fig.add_trace(go.Bar(
                name=status, x=ss["Source"], y=ss["Count"],
                marker_color=STATUS_COLORS.get(status, SLATE),
                text=ss["Count"], textposition="inside",
                textfont=dict(size=13, color="white"),
                marker=dict(line=dict(width=0), cornerradius=4),
            ))
        fig.update_layout(**royal_layout(
            title="Status by Work Category", barmode="stack", height=380,
        ))
        st.plotly_chart(fig, width="stretch")

# ============================================================
# SECTION: Financial Dashboard
# ============================================================
if not filtered.empty:
    st.markdown("""<div class="section-header">
        <span class="icon">&#x1F4B8;</span>
        <span class="text">Financial Dashboard</span>
        <span class="badge">Finance</span>
    </div>""", unsafe_allow_html=True)

    # Gauge row
    total_rev = filtered["Total_Amount"].sum()
    total_coll = filtered["Total_Paid"].sum()
    total_pend = filtered["Balance"].sum()

    if total_rev > 0:
        g1, g2, g3 = st.columns(3)

        with g1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=total_coll,
                number=dict(prefix="INR ", font=dict(size=24, color="#E8E0F5")),
                title=dict(text="Collected", font=dict(size=14, color="#C4B5FD")),
                gauge=dict(
                    axis=dict(range=[0, total_rev], tickfont=dict(size=9, color="#8B7BAA")),
                    bar=dict(color=EMERALD),
                    bgcolor="rgba(30,18,69,0.5)",
                    borderwidth=1, bordercolor="rgba(167,139,250,0.2)",
                    steps=[
                        dict(range=[0, total_rev * 0.5], color="rgba(16,185,129,0.08)"),
                        dict(range=[total_rev * 0.5, total_rev], color="rgba(16,185,129,0.15)"),
                    ],
                ),
            ))
            fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=10),
                              paper_bgcolor="rgba(0,0,0,0)", font=CHART_FONT)
            st.plotly_chart(fig, width="stretch")

        with g2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=total_pend,
                number=dict(prefix="INR ", font=dict(size=24, color="#E8E0F5")),
                title=dict(text="Pending", font=dict(size=14, color="#C4B5FD")),
                gauge=dict(
                    axis=dict(range=[0, total_rev], tickfont=dict(size=9, color="#8B7BAA")),
                    bar=dict(color=ROSE),
                    bgcolor="rgba(30,18,69,0.5)",
                    borderwidth=1, bordercolor="rgba(167,139,250,0.2)",
                    steps=[
                        dict(range=[0, total_rev * 0.5], color="rgba(244,63,94,0.06)"),
                        dict(range=[total_rev * 0.5, total_rev], color="rgba(244,63,94,0.12)"),
                    ],
                ),
            ))
            fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=10),
                              paper_bgcolor="rgba(0,0,0,0)", font=CHART_FONT)
            st.plotly_chart(fig, width="stretch")

        with g3:
            rate = (total_coll / total_rev) * 100
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=rate,
                number=dict(suffix="%", font=dict(size=24, color="#E8E0F5")),
                title=dict(text="Collection Rate", font=dict(size=14, color="#C4B5FD")),
                gauge=dict(
                    axis=dict(range=[0, 100], tickfont=dict(size=9, color="#8B7BAA")),
                    bar=dict(color=ROYAL_VIBRANT),
                    bgcolor="rgba(30,18,69,0.5)",
                    borderwidth=1, bordercolor="rgba(167,139,250,0.2)",
                    steps=[
                        dict(range=[0, 50], color="rgba(124,58,237,0.08)"),
                        dict(range=[50, 100], color="rgba(124,58,237,0.15)"),
                    ],
                    threshold=dict(line=dict(color=GOLD, width=3), thickness=0.75, value=75),
                ),
            ))
            fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=10),
                              paper_bgcolor="rgba(0,0,0,0)", font=CHART_FONT)
            st.plotly_chart(fig, width="stretch")

    # Payment charts
    f1, f2 = st.columns(2)

    with f1:
        fin = filtered[filtered["Total_Amount"] > 0][["Title", "Total_Amount", "Total_Paid", "Balance"]].copy()
        fin["Short"] = fin["Title"].apply(lambda x: x[:35] + "..." if len(x) > 35 else x)
        fin = fin.sort_values("Total_Amount", ascending=True)
        if not fin.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Paid", x=fin["Total_Paid"], y=fin["Short"], orientation="h",
                marker=dict(color=EMERALD, line=dict(width=0), cornerradius=4),
                text=[f"{v/1000:.0f}K" for v in fin["Total_Paid"]], textposition="inside",
                textfont=dict(size=10, color="white"),
            ))
            fig.add_trace(go.Bar(
                name="Balance", x=fin["Balance"], y=fin["Short"], orientation="h",
                marker=dict(color=ROSE, line=dict(width=0), cornerradius=4),
                text=[f"{v/1000:.0f}K" if v > 0 else "" for v in fin["Balance"]], textposition="inside",
                textfont=dict(size=10, color="white"),
            ))
            fig.update_layout(**royal_layout(
                title="Paper-wise Payment Status", barmode="stack", height=440,
                yaxis=dict(tickfont=dict(size=9, color="#C4B5FD")),
            ))
            st.plotly_chart(fig, width="stretch")

    with f2:
        stages = ["1st", "2nd", "3rd", "4th", "5th"]
        vals = [filtered[f"Payment_{i}"].sum() for i in range(1, 6)]
        stage_c = [ROYAL_VIBRANT, ROYAL_MEDIUM, EMERALD, GOLD, ROSE]
        fig = go.Figure(data=[go.Bar(
            x=stages, y=vals,
            marker=dict(color=stage_c, line=dict(width=0), cornerradius=8),
            text=[f"INR {v:,.0f}" if v > 0 else "" for v in vals], textposition="outside",
            textfont=dict(size=11, color="#C4B5FD"),
            width=0.5,
        )])
        fig.update_layout(**royal_layout(
            title="Collections by Payment Stage", height=440,
            yaxis=dict(range=[0, max(vals) * 1.3] if max(vals) > 0 else [0, 100]),
            xaxis=dict(title=dict(text="Payment Stage", font=dict(color="#A78BFA", size=12))),
        ))
        st.plotly_chart(fig, width="stretch")

# ============================================================
# SECTION: Paper Cards (Detailed View)
# ============================================================
if not filtered.empty:
    st.markdown("""<div class="section-header">
        <span class="icon">&#x1F4C4;</span>
        <span class="text">Paper Details</span>
        <span class="badge">All Papers</span>
    </div>""", unsafe_allow_html=True)

    status_css = {
        "Published": "status-published",
        "Accepted": "status-accepted",
        "Communicated to Riya": "status-communicated",
        "Under Review": "status-review",
    }

    for _, paper in filtered.sort_values("SNo").iterrows():
        badge_cls = status_css.get(paper["Status"], "status-communicated")
        paid_str = f"INR {paper['Total_Paid']:,.0f}" if paper["Total_Paid"] > 0 else "Nil"
        bal_str = f"INR {paper['Balance']:,.0f}" if paper["Balance"] > 0 else "Nil"
        st.markdown(f"""
        <div class="paper-item">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:6px;">
                <div style="flex:1; min-width:250px;">
                    <div class="paper-title-text">#{paper['SNo']}. {paper['Title'][:120]}{'...' if len(paper['Title']) > 120 else ''}</div>
                    <div class="paper-meta">
                        &#x1F465; {paper['Author_Names']}
                    </div>
                </div>
                <div style="text-align:right; min-width:150px;">
                    <span class="status-badge {badge_cls}">{paper['Status']}</span>
                    <div class="paper-meta" style="margin-top:6px;">
                        Paid: <b style="color:#6EE7B7;">{paid_str}</b> &bull;
                        Due: <b style="color:#FB7185;">{bal_str}</b>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# SECTION: Client Overview
# ============================================================
if not df_clients.empty:
    st.markdown("""<div class="section-header">
        <span class="icon">&#x1F91D;</span>
        <span class="text">Client Network</span>
        <span class="badge">Clients</span>
    </div>""", unsafe_allow_html=True)

    total_clients = len(df_clients)
    with_papers = df_clients["Paper"].notna().sum() if "Paper" in df_clients.columns else 0
    with_patents = df_clients["Patent"].notna().sum() if "Patent" in df_clients.columns else 0

    cc1, cc2, cc3 = st.columns([1, 1, 2])
    cc1.metric("Total Clients", total_clients)
    cc2.metric("With Papers", int(with_papers))

    with cc3:
        chips = ""
        for _, c in df_clients.iterrows():
            name = c["Name"] if pd.notna(c.get("Name")) else "Unknown"
            chips += f'<span class="client-chip">&#x1F464; {name}</span>'
        st.markdown(f'<div class="client-grid">{chips}</div>', unsafe_allow_html=True)

# ============================================================
# SECTION: Pricing Reference
# ============================================================
if not df_info.empty:
    st.markdown("""<div class="section-header">
        <span class="icon">&#x1F4B3;</span>
        <span class="text">Publication Pricing</span>
        <span class="badge">Reference</span>
    </div>""", unsafe_allow_html=True)

    p1, p2 = st.columns(2)
    with p1:
        st.markdown("""
        <div class="price-card price-sci">
            <div class="price-title" style="color:#C4B5FD;">SCI Publication Package</div>
            <div class="price-total" style="color:#A78BFA;">&#x20B9;60,000</div>
            <div class="price-step"><span style="color:#C4B5FD;">1st &bull; Initial</span><span style="color:#E8E0F5;">&#x20B9;15,000</span></div>
            <div class="price-step"><span style="color:#C4B5FD;">2nd &bull; After Demo</span><span style="color:#E8E0F5;">&#x20B9;15,000</span></div>
            <div class="price-step"><span style="color:#C4B5FD;">3rd &bull; Doc Ready</span><span style="color:#E8E0F5;">&#x20B9;15,000</span></div>
            <div class="price-step"><span style="color:#C4B5FD;">4th &bull; Publication</span><span style="color:#E8E0F5;">&#x20B9;10,000</span></div>
            <div class="price-step"><span style="color:#C4B5FD;">5th &bull; Acceptance</span><span style="color:#E8E0F5;">&#x20B9;5,000</span></div>
        </div>
        """, unsafe_allow_html=True)

    with p2:
        st.markdown("""
        <div class="price-card price-scopus">
            <div class="price-title" style="color:#FCD34D;">Scopus Publication Package</div>
            <div class="price-total" style="color:#F59E0B;">&#x20B9;50,000</div>
            <div class="price-step"><span style="color:#FCD34D;">1st &bull; Initial</span><span style="color:#E8E0F5;">&#x20B9;10,000</span></div>
            <div class="price-step"><span style="color:#FCD34D;">2nd &bull; After Demo</span><span style="color:#E8E0F5;">&#x20B9;15,000</span></div>
            <div class="price-step"><span style="color:#FCD34D;">3rd &bull; Doc Ready</span><span style="color:#E8E0F5;">&#x20B9;15,000</span></div>
            <div class="price-step"><span style="color:#FCD34D;">4th &bull; Publication</span><span style="color:#E8E0F5;">&#x20B9;5,000</span></div>
            <div class="price-step"><span style="color:#FCD34D;">5th &bull; Acceptance</span><span style="color:#E8E0F5;">&#x20B9;5,000</span></div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# SECTION: Full Data Table
# ============================================================
if not filtered.empty:
    st.markdown("""<div class="section-header">
        <span class="icon">&#x1F4CB;</span>
        <span class="text">Complete Data Table</span>
        <span class="badge">Export</span>
    </div>""", unsafe_allow_html=True)

    display_df = filtered[["SNo", "Title", "Author_Names", "Num_Authors",
                           "Total_Amount", "Total_Paid", "Balance", "Status", "Source"]].copy()
    display_df.columns = ["#", "Title", "Authors", "Team", "Total", "Paid", "Balance", "Status", "Category"]
    st.dataframe(display_df.sort_values("#").reset_index(drop=True), width="stretch", height=400)

# ============================================================
# FOOTER
# ============================================================
st.markdown(f"""
<div style='text-align:center; padding: 1.5rem 0 1rem; margin-top: 1rem;
     border-top: 1px solid rgba(167,139,250,0.15);'>
    <div style='font-size: 0.82rem; color: #8B7BAA; font-weight: 500;'>
        Research Publication Tracker &bull; {len(df_papers)} Papers Tracked &bull; Built with Streamlit + Plotly
    </div>
    <div style='font-size: 0.7rem; color: #5B4A7A; margin-top: 4px;'>
        &copy; {datetime.now().year} &bull; Parthasarathy Sundararajan
    </div>
</div>
""", unsafe_allow_html=True)
