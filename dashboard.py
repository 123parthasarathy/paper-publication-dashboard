import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import re

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Paper Publication Dashboard",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# GOOGLE COLOR PALETTE & DESIGN CONSTANTS
# ============================================================
GOOGLE_BLUE = "#4285F4"
GOOGLE_GREEN = "#34A853"
GOOGLE_YELLOW = "#FBBC04"
GOOGLE_RED = "#EA4335"
GOOGLE_PURPLE = "#A142F4"
GOOGLE_CYAN = "#24C1E0"
GOOGLE_ORANGE = "#FA7B17"
GOOGLE_PINK = "#F538A0"

STATUS_COLORS = {
    "Published": GOOGLE_GREEN,
    "Accepted": GOOGLE_BLUE,
    "Communicated to Riya": GOOGLE_YELLOW,
    "Under Review": GOOGLE_ORANGE,
    "Rejected": GOOGLE_RED,
    "In Progress": GOOGLE_CYAN,
    "Other": "#9AA0A6",
}

MULTI_COLORS = [GOOGLE_BLUE, GOOGLE_GREEN, GOOGLE_YELLOW, GOOGLE_RED,
                GOOGLE_PURPLE, GOOGLE_CYAN, GOOGLE_ORANGE, GOOGLE_PINK,
                "#ec4899", "#60a5fa", "#34d399", "#fb923c", "#818cf8",
                "#f472b6", "#a78bfa", "#38bdf8"]

CHART_FONT = dict(family="Google Sans, Segoe UI, Arial, sans-serif", size=13, color="#202124")
TITLE_FONT = dict(family="Google Sans, Segoe UI, Arial, sans-serif", size=20, color="#202124")
CHART_BG = "#FFFFFF"
PLOT_BG = "#FAFAFA"
GRID_COLOR = "rgba(0,0,0,0.06)"

# ============================================================
# CUSTOM CSS - GOOGLE-STYLE THEME
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');

    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #4285F4, #A142F4, #EA4335, #34A853);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 0.8rem 0 0.2rem 0;
        font-family: 'Google Sans', 'Segoe UI', sans-serif;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #5f6368;
        text-align: center;
        margin-bottom: 1.5rem;
        font-family: 'Google Sans', 'Segoe UI', sans-serif;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
        border: 2px solid #e8eaed;
        border-radius: 16px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    div[data-testid="stMetric"] label {
        color: #5f6368 !important;
        font-weight: 500 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #202124 !important;
        font-weight: 700 !important;
    }
    .card-blue { background: linear-gradient(135deg, #4285F4, #5B9CF6); color: white; padding: 1.2rem; border-radius: 14px; text-align: center; margin-bottom: 0.5rem; }
    .card-green { background: linear-gradient(135deg, #34A853, #57BB6D); color: white; padding: 1.2rem; border-radius: 14px; text-align: center; margin-bottom: 0.5rem; }
    .card-yellow { background: linear-gradient(135deg, #FBBC04, #FDD663); color: #202124; padding: 1.2rem; border-radius: 14px; text-align: center; margin-bottom: 0.5rem; }
    .card-red { background: linear-gradient(135deg, #EA4335, #F07068); color: white; padding: 1.2rem; border-radius: 14px; text-align: center; margin-bottom: 0.5rem; }
    .card-purple { background: linear-gradient(135deg, #A142F4, #B86FF6); color: white; padding: 1.2rem; border-radius: 14px; text-align: center; margin-bottom: 0.5rem; }
    .card-cyan { background: linear-gradient(135deg, #24C1E0, #5BD4EB); color: white; padding: 1.2rem; border-radius: 14px; text-align: center; margin-bottom: 0.5rem; }
    .card-value { font-size: 2.2rem; font-weight: 700; }
    .card-label { font-size: 0.85rem; opacity: 0.9; margin-top: 4px; }
    .card-title { font-size: 0.95rem; font-weight: 600; margin-bottom: 6px; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #ede7f6 100%);
    }
    h2, h3 { color: #202124 !important; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# COMMON CHART TEMPLATE
# ============================================================
def base_layout(**kwargs):
    layout = dict(
        template="plotly_white",
        font=CHART_FONT,
        title_font=TITLE_FONT,
        paper_bgcolor=CHART_BG,
        plot_bgcolor=PLOT_BG,
        margin=dict(l=60, r=40, t=110, b=60),
        xaxis=dict(gridcolor=GRID_COLOR, showgrid=True),
        yaxis=dict(gridcolor=GRID_COLOR, showgrid=True),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.05,
            xanchor="center", x=0.5, font=dict(size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
        title=dict(y=0.97),
    )
    layout.update(kwargs)
    return layout


# ============================================================
# DATA LOADING
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def safe_float(val):
    """Convert value to float, handling Indian format like '1,05,000'."""
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
    """Parse a paper work sheet (Sarathy's work or Others work)."""
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

        # Collect authors
        authors = []
        author_amounts = []
        for idx, (name_col, amt_col, email_col) in enumerate([
            (3, 4, 5), (6, 7, 8), (9, 10, 11), (12, 13, 14), (15, 16, 17)
        ]):
            name = str(row.iloc[name_col]).strip() if pd.notna(row.iloc[name_col]) else ""
            amt = safe_float(row.iloc[amt_col])
            email = str(row.iloc[email_col]).strip() if pd.notna(row.iloc[email_col]) else ""
            if name and name.lower() not in ("", "nan", "not available", "-", "can add", "can add authors"):
                authors.append({"name": name, "amount": amt, "email": email})
                author_amounts.append(amt)

        status_raw = str(row.iloc[26]).strip() if len(row) > 26 and pd.notna(row.iloc[26]) else ""
        # Normalize status
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

        paper = {
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
        }
        papers.append(paper)
    return papers


@st.cache_data
def load_data():
    """Load all paper publication data."""
    filepath = os.path.join(BASE_DIR, "Paper-Publishing-Work-In-Progress.xlsx")
    if not os.path.exists(filepath):
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    xl = pd.ExcelFile(filepath)
    all_papers = []

    # Parse main work sheets
    for sheet in xl.sheet_names:
        sl = sheet.lower().strip()
        if "work" in sl:
            papers = parse_paper_sheet(filepath, sheet)
            all_papers.extend(papers)

    df_papers = pd.DataFrame(all_papers) if all_papers else pd.DataFrame()

    # Parse clients
    df_clients = pd.DataFrame()
    if "clients details" in xl.sheet_names:
        df_clients = pd.read_excel(filepath, sheet_name="clients details")

    # Parse pricing info
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
st.sidebar.markdown("## Filters")

if not df_papers.empty:
    # Source filter (Sarathy's work / Others work)
    all_sources = sorted(df_papers["Source"].unique().tolist())
    selected_sources = st.sidebar.multiselect("Work Category", all_sources, default=all_sources)

    # Status filter
    all_statuses = sorted(df_papers["Status"].unique().tolist())
    selected_statuses = st.sidebar.multiselect("Paper Status", all_statuses, default=all_statuses)

    # Author search
    author_search = st.sidebar.text_input("Search Author", "")

    # Paper title search
    title_search = st.sidebar.text_input("Search Paper Title", "")

    # Apply filters
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

st.sidebar.markdown("---")
st.sidebar.markdown("### Data Source")
st.sidebar.info("Edit `Paper-Publishing-Work-In-Progress.xlsx` and refresh to update the dashboard!")

# ============================================================
# HEADER
# ============================================================
st.markdown('<div class="main-header">Paper Publication Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Research Paper Publication Tracking & Analytics &bull; Live from Excel &bull; Auto-updates on refresh</div>',
    unsafe_allow_html=True,
)

# ============================================================
# TOP KPI CARDS (Colored)
# ============================================================
if not df_papers.empty:
    total_papers = len(df_papers)
    published = len(df_papers[df_papers["Status"] == "Published"])
    accepted = len(df_papers[df_papers["Status"] == "Accepted"])
    communicated = len(df_papers[df_papers["Status"] == "Communicated to Riya"])
    total_revenue = df_papers["Total_Amount"].sum()
    total_paid = df_papers["Total_Paid"].sum()
    total_balance = df_papers["Balance"].sum()
else:
    total_papers = published = accepted = communicated = 0
    total_revenue = total_paid = total_balance = 0

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.markdown(f'<div class="card-blue"><div class="card-title">Total Papers</div><div class="card-value">{total_papers}</div><div class="card-label">All Categories</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card-green"><div class="card-title">Published</div><div class="card-value">{published}</div><div class="card-label">Successfully Published</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card-purple"><div class="card-title">Accepted</div><div class="card-value">{accepted}</div><div class="card-label">Awaiting Publication</div></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="card-yellow"><div class="card-title">Communicated</div><div class="card-value">{communicated}</div><div class="card-label">Sent to Riya</div></div>', unsafe_allow_html=True)
c5.markdown(f'<div class="card-cyan"><div class="card-title">Total Paid</div><div class="card-value">{total_paid/1000:.0f}K</div><div class="card-label">INR Collected</div></div>', unsafe_allow_html=True)
c6.markdown(f'<div class="card-red"><div class="card-title">Balance Due</div><div class="card-value">{total_balance/1000:.0f}K</div><div class="card-label">INR Pending</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# KPI METRICS ROW
# ============================================================
if not filtered.empty:
    m1, m2, m3, m4, m5 = st.columns(5)

    # Unique authors across all papers
    all_author_set = set()
    for authors_list in filtered["Authors"]:
        for a in authors_list:
            if a["name"]:
                all_author_set.add(a["name"].lower().strip())

    m1.metric("Filtered Papers", len(filtered))
    m2.metric("Unique Authors", len(all_author_set))
    m3.metric("Avg Authors/Paper", f"{filtered['Num_Authors'].mean():.1f}")
    m4.metric("Total Revenue", f"INR {filtered['Total_Amount'].sum():,.0f}")
    m5.metric("Collection Rate", f"{(filtered['Total_Paid'].sum() / max(filtered['Total_Amount'].sum(), 1)) * 100:.0f}%")

st.markdown("---")

# ============================================================
# ROW 1: Paper Status Distribution + Source Breakdown
# ============================================================
if not filtered.empty:
    st.subheader("Paper Status Overview")
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        status_counts = filtered["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        colors = [STATUS_COLORS.get(s, "#9AA0A6") for s in status_counts["Status"]]

        total = status_counts["Count"].sum()
        custom_text = []
        for _, row in status_counts.iterrows():
            pct = row["Count"] / total * 100
            custom_text.append(f"{row['Count']}<br>({pct:.1f}%)")

        fig = go.Figure(data=[go.Pie(
            labels=status_counts["Status"], values=status_counts["Count"],
            marker=dict(colors=colors, line=dict(color="white", width=3)),
            hole=0.45,
            text=custom_text,
            textinfo="text",
            textposition="inside",
            textfont=dict(size=13, color="white"),
            insidetextorientation="horizontal",
        )])
        fig.update_layout(**base_layout(
            title="Paper Status Distribution", height=450,
            showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.05, xanchor="center", x=0.5, font=dict(size=11)),
        ))
        st.plotly_chart(fig, width="stretch")

    with r1c2:
        # Source-wise status breakdown (stacked bar)
        source_status = filtered.groupby(["Source", "Status"]).size().reset_index(name="Count")
        fig = go.Figure()
        for status in filtered["Status"].unique():
            ss = source_status[source_status["Status"] == status]
            fig.add_trace(go.Bar(
                name=status, x=ss["Source"], y=ss["Count"],
                marker_color=STATUS_COLORS.get(status, "#9AA0A6"),
                text=ss["Count"], textposition="inside",
                textfont=dict(size=13, color="white"),
                marker=dict(line=dict(width=0), cornerradius=4),
            ))
        fig.update_layout(**base_layout(
            title="Status by Work Category", barmode="stack", height=450,
        ))
        st.plotly_chart(fig, width="stretch")

# ============================================================
# ROW 2: Author Contribution Analysis
# ============================================================
if not filtered.empty:
    st.subheader("Author Contribution Analysis")
    r2c1, r2c2 = st.columns(2)

    # Build author stats
    author_stats = {}
    for _, paper in filtered.iterrows():
        for author in paper["Authors"]:
            name = author["name"].strip()
            name_key = name.lower()
            if name_key not in author_stats:
                author_stats[name_key] = {"name": name, "papers": 0, "total_amount": 0}
            author_stats[name_key]["papers"] += 1
            author_stats[name_key]["total_amount"] += author["amount"]

    df_authors = pd.DataFrame(author_stats.values())

    with r2c1:
        # Top authors by paper count
        top_authors = df_authors.sort_values("papers", ascending=True).tail(12)
        colors_a = [MULTI_COLORS[i % len(MULTI_COLORS)] for i in range(len(top_authors))]

        fig = go.Figure(data=[go.Bar(
            x=top_authors["papers"], y=top_authors["name"], orientation="h",
            marker_color=colors_a,
            text=top_authors["papers"], textposition="outside",
            textfont=dict(size=13, color="#202124"),
            marker=dict(line=dict(width=0), cornerradius=5),
        )])
        fig.update_layout(**base_layout(
            title="Authors by Number of Papers", height=480,
            xaxis=dict(gridcolor=GRID_COLOR, dtick=1),
            yaxis=dict(tickfont=dict(size=12, color="#202124")),
        ))
        st.plotly_chart(fig, width="stretch")

    with r2c2:
        # Authors by amount contribution
        top_by_amt = df_authors[df_authors["total_amount"] > 0].sort_values("total_amount", ascending=True).tail(12)
        if not top_by_amt.empty:
            colors_b = [MULTI_COLORS[i % len(MULTI_COLORS)] for i in range(len(top_by_amt))]
            fig = go.Figure(data=[go.Bar(
                x=top_by_amt["total_amount"], y=top_by_amt["name"], orientation="h",
                marker_color=colors_b,
                text=[f"INR {v:,.0f}" for v in top_by_amt["total_amount"]], textposition="outside",
                textfont=dict(size=12, color="#202124"),
                marker=dict(line=dict(width=0), cornerradius=5),
            )])
            fig.update_layout(**base_layout(
                title="Authors by Financial Contribution (INR)", height=480,
                xaxis=dict(gridcolor=GRID_COLOR),
                yaxis=dict(tickfont=dict(size=12, color="#202124")),
            ))
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No financial data available for authors.")

# ============================================================
# ROW 3: Payment Tracking (Waterfall / Bar)
# ============================================================
if not filtered.empty:
    st.subheader("Financial Overview")
    r3c1, r3c2 = st.columns(2)

    with r3c1:
        # Paper-wise financials (Total vs Paid vs Balance)
        fin_data = filtered[filtered["Total_Amount"] > 0][["Title", "Total_Amount", "Total_Paid", "Balance"]].copy()
        fin_data["Short_Title"] = fin_data["Title"].apply(lambda x: x[:40] + "..." if len(x) > 40 else x)
        fin_data = fin_data.sort_values("Total_Amount", ascending=True)

        if not fin_data.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Paid", x=fin_data["Total_Paid"], y=fin_data["Short_Title"],
                orientation="h", marker_color=GOOGLE_GREEN,
                text=[f"{v/1000:.0f}K" for v in fin_data["Total_Paid"]], textposition="inside",
                textfont=dict(size=11, color="white"),
                marker=dict(line=dict(width=0), cornerradius=4),
            ))
            fig.add_trace(go.Bar(
                name="Balance", x=fin_data["Balance"], y=fin_data["Short_Title"],
                orientation="h", marker_color=GOOGLE_RED,
                text=[f"{v/1000:.0f}K" if v > 0 else "" for v in fin_data["Balance"]], textposition="inside",
                textfont=dict(size=11, color="white"),
                marker=dict(line=dict(width=0), cornerradius=4),
            ))
            fig.update_layout(**base_layout(
                title="Paper-wise Payment Status (INR)", barmode="stack", height=500,
                yaxis=dict(tickfont=dict(size=10)),
            ))
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No financial data available.")

    with r3c2:
        # Payment stage breakdown (aggregate)
        stages = ["1st Payment", "2nd Payment", "3rd Payment", "4th Payment", "5th Payment"]
        stage_totals = [
            filtered["Payment_1"].sum(),
            filtered["Payment_2"].sum(),
            filtered["Payment_3"].sum(),
            filtered["Payment_4"].sum(),
            filtered["Payment_5"].sum(),
        ]
        stage_colors = [GOOGLE_BLUE, GOOGLE_GREEN, GOOGLE_PURPLE, GOOGLE_CYAN, GOOGLE_ORANGE]

        fig = go.Figure(data=[go.Bar(
            x=stages, y=stage_totals,
            marker_color=stage_colors,
            text=[f"INR {v:,.0f}" for v in stage_totals], textposition="outside",
            textfont=dict(size=12, color="#202124"),
            marker=dict(line=dict(width=0), cornerradius=6),
            width=0.55,
        )])
        fig.update_layout(**base_layout(
            title="Collections by Payment Stage (INR)", height=500,
            yaxis=dict(range=[0, max(stage_totals) * 1.25] if max(stage_totals) > 0 else [0, 100]),
        ))
        st.plotly_chart(fig, width="stretch")

# ============================================================
# ROW 4: Revenue Summary (Gauge Charts)
# ============================================================
if not filtered.empty and filtered["Total_Amount"].sum() > 0:
    st.subheader("Revenue Summary")
    r4c1, r4c2, r4c3 = st.columns(3)

    total_rev = filtered["Total_Amount"].sum()
    total_collected = filtered["Total_Paid"].sum()
    total_pending = filtered["Balance"].sum()

    with r4c1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_collected,
            number=dict(prefix="INR ", font=dict(size=28)),
            title=dict(text="Total Collected", font=dict(size=16)),
            gauge=dict(
                axis=dict(range=[0, total_rev], tickfont=dict(size=10)),
                bar=dict(color=GOOGLE_GREEN),
                bgcolor="white",
                borderwidth=2,
                bordercolor="#e8eaed",
                steps=[
                    dict(range=[0, total_rev * 0.5], color="#e8f5e9"),
                    dict(range=[total_rev * 0.5, total_rev], color="#c8e6c9"),
                ],
            ),
        ))
        fig.update_layout(height=300, margin=dict(l=30, r=30, t=60, b=20), font=CHART_FONT)
        st.plotly_chart(fig, width="stretch")

    with r4c2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_pending,
            number=dict(prefix="INR ", font=dict(size=28)),
            title=dict(text="Total Pending", font=dict(size=16)),
            gauge=dict(
                axis=dict(range=[0, total_rev], tickfont=dict(size=10)),
                bar=dict(color=GOOGLE_RED),
                bgcolor="white",
                borderwidth=2,
                bordercolor="#e8eaed",
                steps=[
                    dict(range=[0, total_rev * 0.5], color="#ffebee"),
                    dict(range=[total_rev * 0.5, total_rev], color="#ffcdd2"),
                ],
            ),
        ))
        fig.update_layout(height=300, margin=dict(l=30, r=30, t=60, b=20), font=CHART_FONT)
        st.plotly_chart(fig, width="stretch")

    with r4c3:
        collection_pct = (total_collected / total_rev) * 100 if total_rev > 0 else 0
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=collection_pct,
            number=dict(suffix="%", font=dict(size=28)),
            title=dict(text="Collection Rate", font=dict(size=16)),
            gauge=dict(
                axis=dict(range=[0, 100], tickfont=dict(size=10)),
                bar=dict(color=GOOGLE_BLUE),
                bgcolor="white",
                borderwidth=2,
                bordercolor="#e8eaed",
                steps=[
                    dict(range=[0, 50], color="#e3f2fd"),
                    dict(range=[50, 100], color="#bbdefb"),
                ],
                threshold=dict(line=dict(color=GOOGLE_GREEN, width=3), thickness=0.75, value=75),
            ),
        ))
        fig.update_layout(height=300, margin=dict(l=30, r=30, t=60, b=20), font=CHART_FONT)
        st.plotly_chart(fig, width="stretch")

# ============================================================
# ROW 5: Paper Count by Number of Authors + Author Network
# ============================================================
if not filtered.empty:
    st.subheader("Collaboration Analysis")
    r5c1, r5c2 = st.columns(2)

    with r5c1:
        auth_dist = filtered["Num_Authors"].value_counts().sort_index().reset_index()
        auth_dist.columns = ["Num Authors", "Papers"]
        fig = go.Figure(data=[go.Bar(
            x=[f"{n} Author{'s' if n > 1 else ''}" for n in auth_dist["Num Authors"]],
            y=auth_dist["Papers"],
            marker_color=[MULTI_COLORS[i % len(MULTI_COLORS)] for i in range(len(auth_dist))],
            text=auth_dist["Papers"], textposition="outside",
            textfont=dict(size=14, color="#202124"),
            marker=dict(line=dict(width=0), cornerradius=6),
            width=0.5,
        )])
        fig.update_layout(**base_layout(
            title="Papers by Team Size", height=450,
            yaxis=dict(dtick=1, range=[0, auth_dist["Papers"].max() * 1.25]),
        ))
        st.plotly_chart(fig, width="stretch")

    with r5c2:
        # Status progression (funnel-like)
        status_order = ["Communicated to Riya", "Under Review", "Accepted", "Published"]
        status_vals = [len(filtered[filtered["Status"] == s]) for s in status_order]
        fig = go.Figure(data=[go.Funnel(
            y=status_order, x=status_vals,
            textinfo="value+percent initial",
            textfont=dict(size=14),
            marker=dict(
                color=[STATUS_COLORS.get(s, "#9AA0A6") for s in status_order],
                line=dict(width=0),
            ),
            connector=dict(line=dict(color="#e8eaed", width=2)),
        )])
        fig.update_layout(**base_layout(
            title="Publication Pipeline", height=450,
        ))
        st.plotly_chart(fig, width="stretch")

# ============================================================
# ROW 6: Client Overview
# ============================================================
if not df_clients.empty:
    st.subheader("Client Details")
    r6c1, r6c2 = st.columns([2, 1])

    with r6c1:
        st.dataframe(df_clients, width="stretch", height=300)

    with r6c2:
        total_clients = len(df_clients)
        clients_with_papers = df_clients["Paper"].notna().sum() if "Paper" in df_clients.columns else 0
        clients_with_patents = df_clients["Patent"].notna().sum() if "Patent" in df_clients.columns else 0

        st.markdown(f"""
        <div class="card-blue">
            <div class="card-title">Total Clients</div>
            <div class="card-value">{total_clients}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card-green">
            <div class="card-title">With Papers</div>
            <div class="card-value">{clients_with_papers}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card-purple">
            <div class="card-title">With Patents</div>
            <div class="card-value">{clients_with_patents}</div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# ROW 7: Detailed Paper Data Table
# ============================================================
if not filtered.empty:
    st.subheader("Detailed Paper Data")
    st.markdown(f"Showing **{len(filtered)}** papers based on current filters")

    display_df = filtered[["SNo", "Title", "Author_Names", "Num_Authors",
                           "Total_Amount", "Total_Paid", "Balance", "Status", "Source"]].copy()
    display_df.columns = ["#", "Title", "Authors", "Team Size",
                          "Total (INR)", "Paid (INR)", "Balance (INR)", "Status", "Category"]

    st.dataframe(
        display_df.sort_values("#").reset_index(drop=True),
        width="stretch", height=500,
    )

# ============================================================
# ROW 8: Pricing Info
# ============================================================
if not df_info.empty:
    st.subheader("Publication Pricing Reference")
    r8c1, r8c2 = st.columns(2)

    with r8c1:
        st.markdown("""
        <div class="card-blue" style="text-align:left; padding:1.5rem;">
            <div class="card-title" style="font-size:1.1rem;">SCI Publication Package</div>
            <div style="font-size:0.95rem; line-height:1.8; margin-top:0.5rem;">
                Total: <b>INR 60,000</b><br>
                1st: INR 15,000 (Initial)<br>
                2nd: INR 15,000 (After demo)<br>
                3rd: INR 15,000 (Document ready)<br>
                4th: INR 10,000 (Moving to publication)<br>
                5th: INR 5,000 (After acceptance)
            </div>
        </div>
        """, unsafe_allow_html=True)

    with r8c2:
        st.markdown("""
        <div class="card-purple" style="text-align:left; padding:1.5rem;">
            <div class="card-title" style="font-size:1.1rem;">Scopus Publication Package</div>
            <div style="font-size:0.95rem; line-height:1.8; margin-top:0.5rem;">
                Total: <b>INR 50,000</b><br>
                1st: INR 10,000 (Initial)<br>
                2nd: INR 15,000 (After demo)<br>
                3rd: INR 15,000 (Document ready)<br>
                4th: INR 5,000 (Moving to publication)<br>
                5th: INR 5,000 (After acceptance)
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#5f6368; font-size:0.9rem; font-family:Google Sans,sans-serif;'>"
    "<b>Paper Publication Dashboard</b> &bull; "
    f"{len(df_papers)} papers tracked &bull; "
    "Edit the Excel file and refresh to update! &bull; Built with Streamlit + Plotly"
    "</div>",
    unsafe_allow_html=True,
)
