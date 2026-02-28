import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Research Publication Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CLEAN PROFESSIONAL PALETTE
# ============================================================
PRIMARY = "#2563EB"        # Crisp blue
PRIMARY_LIGHT = "#3B82F6"
PRIMARY_SOFT = "#DBEAFE"
PRIMARY_BG = "#EFF6FF"
SECONDARY = "#0F172A"      # Dark navy text
TEXT = "#1E293B"
TEXT_MID = "#475569"
TEXT_LIGHT = "#94A3B8"
BG_WHITE = "#FFFFFF"
BG_PAGE = "#F8FAFC"
BG_CARD = "#FFFFFF"
BORDER = "#E2E8F0"
BORDER_LIGHT = "#F1F5F9"

# Accent colors - professional & clean
EMERALD = "#059669"
EMERALD_LIGHT = "#D1FAE5"
AMBER = "#D97706"
AMBER_LIGHT = "#FEF3C7"
ROSE = "#DC2626"
ROSE_LIGHT = "#FEE2E2"
VIOLET = "#7C3AED"
VIOLET_LIGHT = "#EDE9FE"
TEAL = "#0D9488"
TEAL_LIGHT = "#CCFBF1"
SKY = "#0284C7"
SKY_LIGHT = "#E0F2FE"
INDIGO = "#4F46E5"

STATUS_COLORS = {
    "Published": EMERALD,
    "Accepted": PRIMARY,
    "Communicated to Riya": AMBER,
    "Under Review": TEAL,
    "Rejected": ROSE,
    "In Progress": SKY,
    "Other": TEXT_LIGHT,
}

STATUS_BG = {
    "Published": EMERALD_LIGHT,
    "Accepted": PRIMARY_SOFT,
    "Communicated to Riya": AMBER_LIGHT,
    "Under Review": TEAL_LIGHT,
    "Rejected": ROSE_LIGHT,
    "In Progress": SKY_LIGHT,
    "Other": BORDER_LIGHT,
}

CHART_FONT = dict(family="'Inter', 'Segoe UI', -apple-system, sans-serif", size=12, color=TEXT_MID)
TITLE_FONT = dict(family="'Inter', 'Segoe UI', -apple-system, sans-serif", size=15, color=SECONDARY)

# ============================================================
# CLEAN CSS
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    .stApp { background-color: #F8FAFC; }
    .stApp * { font-family: 'Inter', 'Segoe UI', -apple-system, sans-serif !important; }

    /* Header */
    .dash-header {
        text-align: center; padding: 1.5rem 0 0.2rem;
        font-size: 2.2rem; font-weight: 800; color: #0F172A;
        letter-spacing: -0.03em;
    }
    .dash-header span { color: #2563EB; }
    .dash-sub {
        text-align: center; font-size: 0.88rem; color: #64748B;
        font-weight: 400; margin-bottom: 1.5rem; letter-spacing: 0.01em;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px; padding: 14px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    div[data-testid="stMetric"] label { color: #64748B !important; font-weight: 500 !important; font-size: 0.8rem !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #0F172A !important; font-weight: 700 !important; }

    /* KPI Row */
    .kpi-row { display: flex; gap: 14px; margin-bottom: 1.2rem; flex-wrap: wrap; }
    .kpi-card {
        flex: 1; min-width: 145px; padding: 18px 16px; border-radius: 14px;
        border: 1px solid #E2E8F0; background: #FFFFFF;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: box-shadow 0.2s;
    }
    .kpi-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .kpi-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
    .kpi-icon {
        width: 38px; height: 38px; border-radius: 10px; display: flex;
        align-items: center; justify-content: center; font-size: 1.1rem;
    }
    .kpi-change { font-size: 0.7rem; font-weight: 600; padding: 2px 8px; border-radius: 6px; }
    .kpi-val { font-size: 1.8rem; font-weight: 800; color: #0F172A; line-height: 1; }
    .kpi-label { font-size: 0.78rem; color: #64748B; font-weight: 500; margin-top: 4px; }

    .icon-blue { background: #DBEAFE; }
    .icon-green { background: #D1FAE5; }
    .icon-violet { background: #EDE9FE; }
    .icon-amber { background: #FEF3C7; }
    .icon-sky { background: #E0F2FE; }
    .icon-rose { background: #FEE2E2; }

    /* Section */
    .section-bar {
        display: flex; align-items: center; gap: 8px;
        padding: 8px 0; margin-top: 1rem; margin-bottom: 0.5rem;
        border-bottom: 2px solid #E2E8F0;
    }
    .section-bar .dot { width: 8px; height: 8px; border-radius: 50%; background: #2563EB; }
    .section-bar .title { font-size: 1.05rem; font-weight: 700; color: #0F172A; }
    .section-bar .tag {
        font-size: 0.62rem; background: #EFF6FF; color: #2563EB; padding: 2px 10px;
        border-radius: 6px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;
    }

    /* Paper cards */
    .paper-card {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 14px 18px; margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        transition: border-color 0.15s;
    }
    .paper-card:hover { border-color: #93C5FD; }
    .paper-num { font-size: 0.72rem; font-weight: 700; color: #2563EB; }
    .paper-title { font-size: 0.88rem; font-weight: 600; color: #1E293B; line-height: 1.4; margin: 2px 0 6px; }
    .paper-authors { font-size: 0.78rem; color: #64748B; }
    .paper-finance { font-size: 0.75rem; color: #94A3B8; margin-top: 6px; }
    .paper-finance b { color: #1E293B; }

    .badge {
        display: inline-block; font-size: 0.65rem; font-weight: 600; padding: 3px 10px;
        border-radius: 6px; letter-spacing: 0.02em;
    }
    .badge-published { background: #D1FAE5; color: #065F46; }
    .badge-accepted { background: #DBEAFE; color: #1E40AF; }
    .badge-communicated { background: #FEF3C7; color: #92400E; }
    .badge-review { background: #CCFBF1; color: #115E59; }
    .badge-default { background: #F1F5F9; color: #475569; }

    /* Price cards */
    .price-box {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px;
        padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .price-box-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
    .price-box-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
    .price-box-title { font-size: 0.95rem; font-weight: 700; color: #0F172A; }
    .price-box-total { font-size: 1.5rem; font-weight: 800; margin-bottom: 14px; }
    .price-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 7px 0; border-bottom: 1px solid #F1F5F9; font-size: 0.82rem;
    }
    .price-row:last-child { border-bottom: none; }
    .price-row .step { color: #64748B; font-weight: 500; }
    .price-row .amt { color: #0F172A; font-weight: 600; }

    /* Client chips */
    .chip-grid { display: flex; flex-wrap: wrap; gap: 8px; }
    .chip {
        background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 20px;
        padding: 6px 14px; font-size: 0.8rem; color: #334155; font-weight: 500;
    }

    .divider { border: none; border-top: 1px solid #E2E8F0; margin: 1rem 0; }

    h2, h3 { color: #0F172A !important; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# CHART LAYOUT
# ============================================================
def clean_layout(**kwargs):
    layout = dict(
        template="plotly_white",
        font=CHART_FONT,
        title_font=TITLE_FONT,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=50, r=30, t=70, b=50),
        xaxis=dict(gridcolor="#F1F5F9", showgrid=True, zeroline=False,
                   tickfont=dict(color=TEXT_MID, size=11), linecolor="#E2E8F0"),
        yaxis=dict(gridcolor="#F1F5F9", showgrid=True, zeroline=False,
                   tickfont=dict(color=TEXT_MID, size=11), linecolor="#E2E8F0"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.04,
            xanchor="center", x=0.5, font=dict(size=10, color=TEXT_MID),
            bgcolor="rgba(0,0,0,0)",
        ),
        title=dict(y=0.96),
    )
    layout.update(kwargs)
    return layout


# ============================================================
# DATA LOADING
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
<div style='padding: 8px 0 12px; border-bottom: 1px solid #E2E8F0; margin-bottom: 12px;'>
    <div style='font-size:0.95rem; font-weight:700; color:#0F172A;'>&#x1F4CA; Dashboard Filters</div>
    <div style='font-size:0.72rem; color:#94A3B8; margin-top:2px;'>Refine the data view</div>
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
st.sidebar.markdown(f"<div style='font-size:0.72rem; color:#94A3B8; text-align:center;'>Updated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}</div>", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
st.markdown('<div class="dash-header">Research <span>Publication</span> Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-sub">Comprehensive Paper Publication Tracking &bull; Financial Analytics &bull; Author Insights</div>', unsafe_allow_html=True)

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
    all_auth_set = set()
    for al in df_papers["Authors"]:
        for a in al:
            all_auth_set.add(a["name"].lower().strip())
    unique_authors = len(all_auth_set)
else:
    total_papers = published = accepted = communicated = unique_authors = 0
    total_paid = total_balance = total_revenue = 0

st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card">
        <div class="kpi-top">
            <div class="kpi-icon icon-blue">&#x1F4C4;</div>
        </div>
        <div class="kpi-val">{total_papers}</div>
        <div class="kpi-label">Total Papers</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-top">
            <div class="kpi-icon icon-green">&#x2705;</div>
        </div>
        <div class="kpi-val">{published}</div>
        <div class="kpi-label">Published</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-top">
            <div class="kpi-icon icon-violet">&#x1F3AF;</div>
        </div>
        <div class="kpi-val">{accepted}</div>
        <div class="kpi-label">Accepted</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-top">
            <div class="kpi-icon icon-amber">&#x1F4E8;</div>
        </div>
        <div class="kpi-val">{communicated}</div>
        <div class="kpi-label">Communicated</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-top">
            <div class="kpi-icon icon-sky">&#x1F465;</div>
        </div>
        <div class="kpi-val">{unique_authors}</div>
        <div class="kpi-label">Authors</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-top">
            <div class="kpi-icon icon-rose">&#x20B9;</div>
        </div>
        <div class="kpi-val" style="font-size:1.5rem;">{total_paid/1000:.0f}K / {(total_paid+total_balance)/1000:.0f}K</div>
        <div class="kpi-label">Collected / Total (INR)</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Metric row
if not filtered.empty:
    filt_auth = set()
    for al in filtered["Authors"]:
        for a in al:
            filt_auth.add(a["name"].lower().strip())
    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
    mc1.metric("Filtered Papers", len(filtered))
    mc2.metric("Unique Authors", len(filt_auth))
    mc3.metric("Avg Team Size", f"{filtered['Num_Authors'].mean():.1f}")
    mc4.metric("Revenue", f"INR {filtered['Total_Amount'].sum():,.0f}")
    rate = (filtered['Total_Paid'].sum() / max(filtered['Total_Amount'].sum(), 1)) * 100
    mc5.metric("Collection Rate", f"{rate:.0f}%")

# ============================================================
# SECTION: Status Overview
# ============================================================
if not filtered.empty:
    st.markdown("""<div class="section-bar">
        <div class="dot"></div><div class="title">Status Overview</div><div class="tag">Analytics</div>
    </div>""", unsafe_allow_html=True)

    r1a, r1b = st.columns(2)

    with r1a:
        sc = filtered["Status"].value_counts().reset_index()
        sc.columns = ["Status", "Count"]
        colors = [STATUS_COLORS.get(s, TEXT_LIGHT) for s in sc["Status"]]
        total = sc["Count"].sum()

        fig = go.Figure(data=[go.Pie(
            labels=sc["Status"], values=sc["Count"],
            marker=dict(colors=colors, line=dict(color="white", width=3)),
            hole=0.5,
            textinfo="value",
            textfont=dict(size=15, color="white", family="Inter"),
            hovertemplate="<b>%{label}</b><br>%{value} papers (%{percent})<extra></extra>",
        )])
        fig.add_annotation(text=f"<b>{total}</b><br><span style='font-size:11px'>Total</span>",
                           x=0.5, y=0.5, font=dict(size=26, color=SECONDARY), showarrow=False)
        fig.update_layout(**clean_layout(
            title="Paper Status Distribution", height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.02, x=0.5, xanchor="center"),
        ))
        st.plotly_chart(fig, width="stretch")

    with r1b:
        status_order = ["Communicated to Riya", "Under Review", "Accepted", "Published"]
        status_vals = [len(filtered[filtered["Status"] == s]) for s in status_order]
        labels = ["Communicated", "Under Review", "Accepted", "Published"]

        fig = go.Figure(data=[go.Funnel(
            y=labels, x=status_vals,
            textinfo="value+percent initial",
            textfont=dict(size=14, color="white"),
            marker=dict(
                color=[STATUS_COLORS.get(s, TEXT_LIGHT) for s in status_order],
                line=dict(width=1, color="white"),
            ),
            connector=dict(line=dict(color="#E2E8F0", width=2)),
        )])
        fig.update_layout(**clean_layout(title="Publication Pipeline", height=400))
        st.plotly_chart(fig, width="stretch")

# ============================================================
# SECTION: Author Analysis
# ============================================================
if not filtered.empty:
    st.markdown("""<div class="section-bar">
        <div class="dot" style="background:#059669;"></div><div class="title">Author Analysis</div><div class="tag">Research</div>
    </div>""", unsafe_allow_html=True)

    author_stats = {}
    for _, paper in filtered.iterrows():
        for author in paper["Authors"]:
            key = author["name"].strip().lower()
            if key not in author_stats:
                author_stats[key] = {"name": author["name"].strip(), "papers": 0, "amount": 0}
            author_stats[key]["papers"] += 1
            author_stats[key]["amount"] += author["amount"]
    df_auth = pd.DataFrame(author_stats.values())

    a1, a2 = st.columns(2)

    with a1:
        top = df_auth.sort_values("papers", ascending=True).tail(12)
        n = len(top)
        # Soft blue gradient
        colors = [f"rgba(37,99,235,{0.35 + 0.65 * i / max(n-1,1)})" for i in range(n)]
        fig = go.Figure(data=[go.Bar(
            x=top["papers"], y=top["name"], orientation="h",
            marker=dict(color=colors, line=dict(width=0), cornerradius=6),
            text=top["papers"], textposition="outside",
            textfont=dict(size=12, color=TEXT),
        )])
        fig.update_layout(**clean_layout(
            title="Top Authors by Paper Count", height=420,
            xaxis=dict(dtick=1, gridcolor="#F1F5F9"),
            yaxis=dict(tickfont=dict(size=11, color=TEXT)),
        ))
        st.plotly_chart(fig, width="stretch")

    with a2:
        top_amt = df_auth[df_auth["amount"] > 0].sort_values("amount", ascending=True).tail(12)
        if not top_amt.empty:
            n2 = len(top_amt)
            colors2 = [f"rgba(5,150,105,{0.35 + 0.65 * i / max(n2-1,1)})" for i in range(n2)]
            fig = go.Figure(data=[go.Bar(
                x=top_amt["amount"], y=top_amt["name"], orientation="h",
                marker=dict(color=colors2, line=dict(width=0), cornerradius=6),
                text=[f"INR {v:,.0f}" for v in top_amt["amount"]], textposition="outside",
                textfont=dict(size=11, color=TEXT),
            )])
            fig.update_layout(**clean_layout(
                title="Authors by Financial Contribution", height=420,
                yaxis=dict(tickfont=dict(size=11, color=TEXT)),
            ))
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No financial data available.")

    # Team size + Source breakdown
    b1, b2 = st.columns(2)

    with b1:
        ad = filtered["Num_Authors"].value_counts().sort_index().reset_index()
        ad.columns = ["Num", "Papers"]
        tc = [PRIMARY, EMERALD, AMBER, VIOLET, TEAL, SKY]
        fig = go.Figure(data=[go.Bar(
            x=[f"{n} Author{'s' if n > 1 else ''}" for n in ad["Num"]],
            y=ad["Papers"],
            marker=dict(color=[tc[i % len(tc)] for i in range(len(ad))],
                        line=dict(width=0), cornerradius=8),
            text=ad["Papers"], textposition="outside",
            textfont=dict(size=13, color=TEXT), width=0.5,
        )])
        fig.update_layout(**clean_layout(
            title="Papers by Team Size", height=370,
            yaxis=dict(dtick=1, range=[0, ad["Papers"].max() * 1.3]),
        ))
        st.plotly_chart(fig, width="stretch")

    with b2:
        ss = filtered.groupby(["Source", "Status"]).size().reset_index(name="Count")
        fig = go.Figure()
        for status in filtered["Status"].unique():
            d = ss[ss["Status"] == status]
            fig.add_trace(go.Bar(
                name=status, x=d["Source"], y=d["Count"],
                marker_color=STATUS_COLORS.get(status, TEXT_LIGHT),
                text=d["Count"], textposition="inside",
                textfont=dict(size=12, color="white"),
                marker=dict(line=dict(width=0), cornerradius=4),
            ))
        fig.update_layout(**clean_layout(
            title="Status by Work Category", barmode="stack", height=370,
        ))
        st.plotly_chart(fig, width="stretch")

# ============================================================
# SECTION: Financial Dashboard
# ============================================================
if not filtered.empty:
    st.markdown("""<div class="section-bar">
        <div class="dot" style="background:#D97706;"></div><div class="title">Financial Dashboard</div><div class="tag">Finance</div>
    </div>""", unsafe_allow_html=True)

    total_rev = filtered["Total_Amount"].sum()
    total_coll = filtered["Total_Paid"].sum()
    total_pend = filtered["Balance"].sum()

    if total_rev > 0:
        g1, g2, g3 = st.columns(3)
        gauge_configs = [
            (g1, total_coll, "Collected", EMERALD, "INR "),
            (g2, total_pend, "Pending", ROSE, "INR "),
            (g3, (total_coll / total_rev) * 100, "Collection Rate", PRIMARY, ""),
        ]
        for col, val, label, color, prefix in gauge_configs:
            with col:
                max_val = total_rev if prefix else 100
                suffix = "" if prefix else "%"
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=val,
                    number=dict(prefix=prefix, suffix=suffix, font=dict(size=22, color=SECONDARY)),
                    title=dict(text=label, font=dict(size=13, color=TEXT_MID)),
                    gauge=dict(
                        axis=dict(range=[0, max_val], tickfont=dict(size=9, color=TEXT_LIGHT), showticklabels=False),
                        bar=dict(color=color, thickness=0.75),
                        bgcolor="#F1F5F9",
                        borderwidth=0,
                        steps=[dict(range=[0, max_val], color="#F8FAFC")],
                    ),
                ))
                fig.update_layout(height=220, margin=dict(l=20, r=20, t=50, b=10),
                                  paper_bgcolor="rgba(0,0,0,0)", font=CHART_FONT)
                st.plotly_chart(fig, width="stretch")

    f1, f2 = st.columns(2)

    with f1:
        fin = filtered[filtered["Total_Amount"] > 0][["Title","Total_Amount","Total_Paid","Balance"]].copy()
        fin["Short"] = fin["Title"].apply(lambda x: x[:35] + "..." if len(x) > 35 else x)
        fin = fin.sort_values("Total_Amount", ascending=True)
        if not fin.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Paid", x=fin["Total_Paid"], y=fin["Short"], orientation="h",
                marker=dict(color=EMERALD, line=dict(width=0), cornerradius=4),
                text=[f"{v/1000:.0f}K" for v in fin["Total_Paid"]], textposition="inside",
                textfont=dict(size=10, color="white")))
            fig.add_trace(go.Bar(name="Balance", x=fin["Balance"], y=fin["Short"], orientation="h",
                marker=dict(color=ROSE, line=dict(width=0), cornerradius=4),
                text=[f"{v/1000:.0f}K" if v > 0 else "" for v in fin["Balance"]], textposition="inside",
                textfont=dict(size=10, color="white")))
            fig.update_layout(**clean_layout(
                title="Paper-wise Payment Status", barmode="stack", height=420,
                yaxis=dict(tickfont=dict(size=9, color=TEXT_MID)),
            ))
            st.plotly_chart(fig, width="stretch")

    with f2:
        stages = ["1st", "2nd", "3rd", "4th", "5th"]
        vals = [filtered[f"Payment_{i}"].sum() for i in range(1,6)]
        sc = [PRIMARY, EMERALD, VIOLET, AMBER, TEAL]
        fig = go.Figure(data=[go.Bar(
            x=stages, y=vals,
            marker=dict(color=sc, line=dict(width=0), cornerradius=8),
            text=[f"INR {v:,.0f}" if v > 0 else "" for v in vals], textposition="outside",
            textfont=dict(size=11, color=TEXT), width=0.5,
        )])
        fig.update_layout(**clean_layout(
            title="Collections by Payment Stage", height=420,
            yaxis=dict(range=[0, max(vals)*1.3] if max(vals) > 0 else [0, 100]),
            xaxis=dict(title=dict(text="Payment Stage", font=dict(color=TEXT_MID, size=11))),
        ))
        st.plotly_chart(fig, width="stretch")

# ============================================================
# SECTION: Paper Details
# ============================================================
if not filtered.empty:
    st.markdown("""<div class="section-bar">
        <div class="dot" style="background:#7C3AED;"></div><div class="title">Paper Details</div><div class="tag">All Papers</div>
    </div>""", unsafe_allow_html=True)

    badge_map = {
        "Published": "badge-published", "Accepted": "badge-accepted",
        "Communicated to Riya": "badge-communicated", "Under Review": "badge-review",
    }

    for _, p in filtered.sort_values("SNo").iterrows():
        bcls = badge_map.get(p["Status"], "badge-default")
        paid = f"INR {p['Total_Paid']:,.0f}" if p["Total_Paid"] > 0 else "---"
        bal = f"INR {p['Balance']:,.0f}" if p["Balance"] > 0 else "---"
        title_text = p["Title"][:130] + ("..." if len(p["Title"]) > 130 else "")
        st.markdown(f"""
        <div class="paper-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px;">
                <div style="flex:1; min-width:280px;">
                    <div class="paper-num">PAPER #{p['SNo']} &bull; {p['Source']}</div>
                    <div class="paper-title">{title_text}</div>
                    <div class="paper-authors">&#x1F465; {p['Author_Names']}</div>
                </div>
                <div style="text-align:right;">
                    <span class="badge {bcls}">{p['Status']}</span>
                    <div class="paper-finance">
                        Paid: <b style="color:{EMERALD};">{paid}</b> &nbsp;&bull;&nbsp;
                        Due: <b style="color:{ROSE};">{bal}</b>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# SECTION: Clients
# ============================================================
if not df_clients.empty:
    st.markdown("""<div class="section-bar">
        <div class="dot" style="background:#0D9488;"></div><div class="title">Client Network</div><div class="tag">Clients</div>
    </div>""", unsafe_allow_html=True)

    cc1, cc2, cc3 = st.columns([1, 1, 3])
    total_cl = len(df_clients)
    with_p = int(df_clients["Paper"].notna().sum()) if "Paper" in df_clients.columns else 0
    cc1.metric("Total Clients", total_cl)
    cc2.metric("With Papers", with_p)

    with cc3:
        chips = ""
        for _, c in df_clients.iterrows():
            name = c["Name"] if pd.notna(c.get("Name")) else "Unknown"
            chips += f'<span class="chip">&#x1F464; {name}</span>'
        st.markdown(f'<div class="chip-grid">{chips}</div>', unsafe_allow_html=True)

# ============================================================
# SECTION: Pricing
# ============================================================
if not df_info.empty:
    st.markdown("""<div class="section-bar">
        <div class="dot" style="background:#4F46E5;"></div><div class="title">Publication Pricing</div><div class="tag">Reference</div>
    </div>""", unsafe_allow_html=True)

    p1, p2 = st.columns(2)
    with p1:
        st.markdown(f"""
        <div class="price-box">
            <div class="price-box-header">
                <div class="price-box-icon icon-blue">&#x1F4D8;</div>
                <div class="price-box-title">SCI Publication</div>
            </div>
            <div class="price-box-total" style="color:{PRIMARY};">&#x20B9; 60,000</div>
            <div class="price-row"><span class="step">1st &bull; Initial Payment</span><span class="amt">&#x20B9;15,000</span></div>
            <div class="price-row"><span class="step">2nd &bull; After Demo</span><span class="amt">&#x20B9;15,000</span></div>
            <div class="price-row"><span class="step">3rd &bull; Document Ready</span><span class="amt">&#x20B9;15,000</span></div>
            <div class="price-row"><span class="step">4th &bull; Moving to Publication</span><span class="amt">&#x20B9;10,000</span></div>
            <div class="price-row"><span class="step">5th &bull; After Acceptance</span><span class="amt">&#x20B9;5,000</span></div>
        </div>
        """, unsafe_allow_html=True)

    with p2:
        st.markdown(f"""
        <div class="price-box">
            <div class="price-box-header">
                <div class="price-box-icon icon-amber">&#x1F4D9;</div>
                <div class="price-box-title">Scopus Publication</div>
            </div>
            <div class="price-box-total" style="color:{AMBER};">&#x20B9; 50,000</div>
            <div class="price-row"><span class="step">1st &bull; Initial Payment</span><span class="amt">&#x20B9;10,000</span></div>
            <div class="price-row"><span class="step">2nd &bull; After Demo</span><span class="amt">&#x20B9;15,000</span></div>
            <div class="price-row"><span class="step">3rd &bull; Document Ready</span><span class="amt">&#x20B9;15,000</span></div>
            <div class="price-row"><span class="step">4th &bull; Moving to Publication</span><span class="amt">&#x20B9;5,000</span></div>
            <div class="price-row"><span class="step">5th &bull; After Acceptance</span><span class="amt">&#x20B9;5,000</span></div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# SECTION: Data Table
# ============================================================
if not filtered.empty:
    st.markdown("""<div class="section-bar">
        <div class="dot" style="background:#64748B;"></div><div class="title">Complete Data</div><div class="tag">Table</div>
    </div>""", unsafe_allow_html=True)

    disp = filtered[["SNo","Title","Author_Names","Num_Authors",
                      "Total_Amount","Total_Paid","Balance","Status","Source"]].copy()
    disp.columns = ["#","Title","Authors","Team","Total (INR)","Paid (INR)","Balance (INR)","Status","Category"]
    st.dataframe(disp.sort_values("#").reset_index(drop=True), width="stretch", height=400)

# ============================================================
# FOOTER
# ============================================================
st.markdown(f"""
<div style='text-align:center; padding: 1.5rem 0 1rem; margin-top: 1.5rem;
     border-top: 1px solid #E2E8F0;'>
    <div style='font-size: 0.82rem; color: #94A3B8; font-weight: 500;'>
        Research Publication Tracker &bull; {len(df_papers)} Papers &bull; Built with Streamlit + Plotly
    </div>
    <div style='font-size: 0.7rem; color: #CBD5E1; margin-top: 4px;'>
        &copy; {datetime.now().year} Parthasarathy Sundararajan
    </div>
</div>
""", unsafe_allow_html=True)
