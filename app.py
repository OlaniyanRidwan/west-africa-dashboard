import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# -----------------------------------
# PAGE CONFIG (must be called ONCE, first)
# -----------------------------------
st.set_page_config(
    page_title="West Africa Economic Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------
# CUSTOM STYLING
# -----------------------------------

st.markdown("""
<style>
    h1 { font-weight: 800; letter-spacing: -1px; }

    div[data-testid="stMetric"] {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 14px;
        padding: 18px 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px;
        opacity: 0.85;
        color: var(--text-color) !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 26px;
        font-weight: 700;
        color: var(--text-color) !important;
    }

    /* ---- TAB STYLING ---- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        padding: 6px;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.25);
        transition: all 0.2s ease-in-out;
    }

    .stTabs [data-baseweb="tab"] p {
        color: var(--text-color) !important;
        font-weight: 500;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(37, 99, 235, 0.15);
    }

    /* Active/selected tab — solid blue with WHITE text for guaranteed contrast */
    .stTabs [aria-selected="true"] {
        background: #2563eb !important;
        border: 1px solid #3b82f6 !important;
        box-shadow: 0 2px 10px rgba(37, 99, 235, 0.35);
    }

    .stTabs [aria-selected="true"] p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Insight box styling */
    .insight-box {
        background: rgba(34, 197, 94, 0.10);
        border-left: 4px solid #22c55e;
        border-radius: 10px;
        padding: 16px 20px;
        margin-top: 10px;
        color: var(--text-color) !important;
    }
    .insight-box b {
        color: var(--text-color) !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# LOAD DATA
# -----------------------------------
DATA_PATH = os.path.join("data", "west_africa_master_dataset.csv")

@st.cache_data
def load_data(path):
    if not os.path.exists(path):
        st.error(f"⚠️ Data file not found at `{path}`. Update DATA_PATH to match your folder structure.")
        st.stop()
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    return df

df = load_data(DATA_PATH)

# -----------------------------------
# HEADER
# -----------------------------------
st.title("🌍 West Africa Economic Dashboard")
st.markdown(
    "An interactive dashboard exploring **Population, GDP, Inflation and CPI** "
    "across West African countries (2001–2025)."
)
st.markdown("---")

# -----------------------------------
# SIDEBAR FILTERS
# -----------------------------------
st.sidebar.header("🔎 Dashboard Filters")

all_countries = sorted(df["Country"].unique())
country = st.sidebar.multiselect(
    "Select Countries",
    all_countries,
    default=all_countries
)

year = st.sidebar.slider(
    "Select Year",
    int(df.Year.min()),
    int(df.Year.max()),
    int(df.Year.max())
)

st.sidebar.markdown("---")
st.sidebar.caption("Tip: use the multiselect to compare a smaller subset of countries — trend lines get easier to read.")

if not country:
    st.warning("Please select at least one country from the sidebar.")
    st.stop()

filtered = df[(df.Country.isin(country)) & (df.Year == year)]
trend = df[df.Country.isin(country)]

# -----------------------------------
# KPI CARDS
# -----------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("👥 Total Population", f"{filtered.Population.sum()/1e6:.1f} M")

with col2:
    st.metric("💰 Average GDP", f"${filtered.GDP.mean():,.0f}")

with col3:
    st.metric("📈 Avg Inflation", f"{filtered.Inflation.mean():.2f}%")

with col4:
    st.metric("🌍 Countries Selected", filtered.Country.nunique())

st.markdown("---")

# -----------------------------------
# TABS FOR CLEAN NAVIGATION
# -----------------------------------
tab_pop, tab_econ, tab_inf, tab_growth, tab_rel, tab_data = st.tabs(
    ["👥 Population", "💰 Economy", "📈 Inflation", "📊 Growth Analysis", "🔗 Relationships", "📄 Dataset"]
)
def insight_box(markdown_text):
    st.markdown(f'<div class="insight-box">{markdown_text}</div>', unsafe_allow_html=True)

# ===== POPULATION TAB =====
with tab_pop:
    left, right = st.columns(2)

    fig = px.choropleth(
        filtered,
        locations="Country Code",
        color="Population",
        hover_name="Country",
        color_continuous_scale="YlOrRd",
        projection="natural earth",
        title=f"Population by Country ({year})"
    )
    fig.update_geos(
        lataxis_range=[0, 25],
        lonaxis_range=[-20, 20],
        showcountries=True,
        showframe=False,
        showcoastlines=False
    )
    fig.update_layout(template="plotly_dark", margin=dict(l=0, r=0, t=40, b=0))
    left.plotly_chart(fig, use_container_width=True)

    fig = px.line(
        trend, x="Year", y="Population", color="Country",
        template="plotly_dark", title="Population Trend Over Time",
        markers=True
    )
    right.plotly_chart(fig, use_container_width=True)

    fig = px.treemap(
        filtered, path=["Country"], values="Population",
        color="Population", color_continuous_scale="YlOrRd",
        title=f"Population Share ({year})"
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # ---- Key Insights ----
    largest = filtered.loc[filtered.Population.idxmax()]
    smallest = filtered.loc[filtered.Population.idxmin()]
    growth = (
        trend.groupby("Country")["Population"]
        .agg(lambda s: s.iloc[-1] - s.iloc[0])
        .sort_values(ascending=False)
    )
    fastest_growing = growth.index[0]

    st.subheader("🔑 Key Insights")
    insight_box(f"""
    • <b>{largest.Country}</b> has the largest population in <b>{year}</b> ({largest.Population/1e6:.1f}M).<br>
    • <b>{smallest.Country}</b> has the smallest population in <b>{year}</b> ({smallest.Population/1e6:.1f}M).<br>
    • <b>{fastest_growing}</b> has added the most people over the selected period.<br>
    • Combined population across selected countries: <b>{filtered.Population.sum()/1e6:.1f}M</b>.
    """)

# ===== ECONOMY TAB =====
with tab_econ:
    left, right = st.columns(2)

    rank = filtered.sort_values("GDP")
    fig = px.bar(
        rank, x="GDP", y="Country", orientation="h",
        color="GDP", color_continuous_scale="Blues",
        template="plotly_dark", title=f"GDP Ranking ({year})", text_auto=".2s"
    )
    left.plotly_chart(fig, use_container_width=True)

    fig = px.line(
        trend, x="Year", y="GDP", color="Country",
        template="plotly_dark", title="GDP Trend Over Time", markers=True
    )
    right.plotly_chart(fig, use_container_width=True)

    gdp_pc = trend.copy()
    gdp_pc["GDP per Capita"] = gdp_pc["GDP"] / gdp_pc["Population"]
    fig = px.area(
        gdp_pc, x="Year", y="GDP per Capita", color="Country",
        template="plotly_dark", title="GDP per Capita Trend"
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---- Key Insights ----
    highest_gdp = filtered.loc[filtered.GDP.idxmax()]
    lowest_gdp = filtered.loc[filtered.GDP.idxmin()]
    gdp_pc_now = gdp_pc[gdp_pc.Year == year]
    highest_pc = gdp_pc_now.loc[gdp_pc_now["GDP per Capita"].idxmax()]

    st.subheader("🔑 Key Insights")
    insight_box(f"""
    • <b>{highest_gdp.Country}</b> recorded the highest total GDP in <b>{year}</b>.<br>
    • <b>{lowest_gdp.Country}</b> recorded the lowest total GDP in <b>{year}</b>.<br>
    • <b>{highest_pc.Country}</b> leads in GDP per capita among selected countries.<br>
    • Average GDP across selected countries: <b>${filtered.GDP.mean():,.0f}</b>.
    """)

# ===== INFLATION TAB =====
with tab_inf:
    left, right = st.columns(2)

    pivot = trend.pivot_table(index="Country", columns="Year", values="Inflation")
    fig = px.imshow(
        pivot, color_continuous_scale="RdYlBu_r", aspect="auto",
        title="Inflation Heatmap (Country x Year)"
    )
    fig.update_layout(template="plotly_dark")
    left.plotly_chart(fig, use_container_width=True)

    fig = px.line(
        trend, x="Year", y="Inflation", color="Country",
        template="plotly_dark", title="Inflation Trend Over Time", markers=True
    )
    right.plotly_chart(fig, use_container_width=True)

    fig = px.box(
        trend, x="Country", y="Inflation", color="Country",
        template="plotly_dark", title="Inflation Volatility by Country (All Years)"
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # ---- Key Insights ----
    highest_inf = filtered.loc[filtered.Inflation.idxmax()]
    lowest_inf = filtered.loc[filtered.Inflation.idxmin()]
    volatility = trend.groupby("Country")["Inflation"].std().sort_values(ascending=False)
    most_volatile = volatility.index[0]

    st.subheader("🔑 Key Insights")
    insight_box(f"""
    • <b>{highest_inf.Country}</b> has the highest inflation rate in <b>{year}</b> ({highest_inf.Inflation:.2f}%).<br>
    • <b>{lowest_inf.Country}</b> has the lowest inflation rate in <b>{year}</b> ({lowest_inf.Inflation:.2f}%).<br>
    • <b>{most_volatile}</b> shows the most inflation volatility historically.<br>
    • Average regional inflation in <b>{year}</b>: <b>{filtered.Inflation.mean():.2f}%</b>.
    """)

# ===== GROWTH ANALYSIS TAB =====
with tab_growth:
    st.markdown("Analyzing **year-over-year population growth** and its relationship with GDP growth.")

    # ---- Compute growth rates ----
    growth_df = trend.sort_values(["Country", "Year"]).copy()
    growth_df["Pop_Growth_%"] = growth_df.groupby("Country")["Population"].pct_change() * 100
    growth_df["GDP_Growth_%"] = growth_df.groupby("Country")["GDP"].pct_change() * 100
    growth_df = growth_df.dropna(subset=["Pop_Growth_%", "GDP_Growth_%"])

    left, right = st.columns(2)

    # Chart 1: Population growth trend
    fig = px.line(
        growth_df, x="Year", y="Pop_Growth_%", color="Country",
        template="plotly_dark", title="Population Growth Rate (% YoY)", markers=True
    )
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    left.plotly_chart(fig, use_container_width=True)

    # Chart 2: GDP growth trend (for comparison)
    fig = px.line(
        growth_df, x="Year", y="GDP_Growth_%", color="Country",
        template="plotly_dark", title="GDP Growth Rate (% YoY)", markers=True
    )
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    right.plotly_chart(fig, use_container_width=True)

    # Chart 3: Scatter with OLS trendline — Pop growth vs GDP growth (same year)
    st.markdown("#### Population Growth vs GDP Growth (Same Year)")
    try:
        fig = px.scatter(
            growth_df, x="Pop_Growth_%", y="GDP_Growth_%", color="Country",
            trendline="ols", trendline_scope="overall",
            template="plotly_dark",
            title="Does Faster Population Growth Correlate With Faster GDP Growth?",
            hover_data=["Year"]
        )
        st.plotly_chart(fig, use_container_width=True)

        # Pull R² and slope from the trendline model
        results = px.get_trendline_results(fig)
        model = results.iloc[0]["px_fit_results"]
        slope = model.params[1]
        r_squared = model.rsquared
        p_value = model.pvalues[1]
    except Exception:
        st.warning("⚠️ Trendline requires the `statsmodels` package. Run `pip install statsmodels` to enable regression stats.")
        slope, r_squared, p_value = None, None, None

    # Chart 4: Lag effect — this year's pop growth vs NEXT year's GDP growth
    st.markdown("#### Lag Effect: This Year's Population Growth vs Next Year's GDP Growth")
    lag_df = growth_df.copy()
    lag_df["Next_Year_GDP_Growth_%"] = lag_df.groupby("Country")["GDP_Growth_%"].shift(-1)
    lag_df = lag_df.dropna(subset=["Next_Year_GDP_Growth_%"])

    fig = px.scatter(
        lag_df, x="Pop_Growth_%", y="Next_Year_GDP_Growth_%", color="Country",
        trendline="ols", trendline_scope="overall",
        template="plotly_dark",
        title="Population Growth → GDP Growth the FOLLOWING Year",
        hover_data=["Year"]
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---- Key Insights ----
    st.subheader("🔑 Key Insights")

    avg_pop_growth = growth_df["Pop_Growth_%"].mean()
    avg_gdp_growth = growth_df["GDP_Growth_%"].mean()
    fastest_pop = growth_df.groupby("Country")["Pop_Growth_%"].mean().idxmax()
    fastest_gdp = growth_df.groupby("Country")["GDP_Growth_%"].mean().idxmax()

    insight_text = f"""
    • Average population growth across selected countries: <b>{avg_pop_growth:.2f}% per year</b>.<br>
    • Average GDP growth across selected countries: <b>{avg_gdp_growth:.2f}% per year</b>.<br>
    • <b>{fastest_pop}</b> has the fastest average population growth.<br>
    • <b>{fastest_gdp}</b> has the fastest average GDP growth.<br>
    """

    if r_squared is not None:
        direction = "positively" if slope > 0 else "negatively"
        significance = "statistically significant" if p_value < 0.05 else "not statistically significant at the 5% level"
        insight_text += f"""
    • A simple regression shows population growth is <b>{direction}</b> associated with GDP growth
      (R² = <b>{r_squared:.3f}</b>, this relationship is <b>{significance}</b>).<br>
    • For every 1% increase in population growth, GDP growth changes by approximately <b>{slope:.2f} percentage points</b>, holding the overall trend fixed.
    """
    else:
        insight_text += "• Install `statsmodels` to see regression strength (R²) and significance testing."

    insight_box(insight_text)

# ===== RELATIONSHIPS TAB =====
with tab_rel:
    left, right = st.columns(2)

    fig = px.scatter(
        filtered, x="Population", y="GDP", color="Inflation", size="Population",
        hover_name="Country", template="plotly_dark",
        color_continuous_scale="Turbo", title=f"Population vs GDP vs Inflation ({year})"
    )
    left.plotly_chart(fig, use_container_width=True)

    corr_cols = ["Population", "GDP", "Inflation"]
    if "CPI" in filtered.columns:
        corr_cols.append("CPI")

    corr = filtered[corr_cols].corr()
    fig = px.imshow(
        corr, text_auto=True, color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1, title="Correlation Matrix"
    )
    fig.update_layout(template="plotly_dark")
    right.plotly_chart(fig, use_container_width=True)

    if len(country) <= 6:
        radar_df = filtered[["Country"] + corr_cols].copy()
        for col in corr_cols:
            rng = radar_df[col].max() - radar_df[col].min()
            radar_df[col] = (radar_df[col] - radar_df[col].min()) / rng if rng != 0 else 0.5

        fig = go.Figure()
        for _, row in radar_df.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row[c] for c in corr_cols] + [row[corr_cols[0]]],
                theta=corr_cols + [corr_cols[0]],
                fill="toself", name=row.Country
            ))
        fig.update_layout(
            template="plotly_dark",
            title=f"Normalized Country Comparison ({year})",
            polar=dict(radialaxis=dict(visible=True, range=[0, 1]))
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select 6 or fewer countries to view the radar comparison chart.")

    # ---- NEW CHART 1: CPI vs Inflation trend ----
    left2, right2 = st.columns(2)

    if "CPI" in trend.columns:
        fig = px.line(
            trend, x="Year", y="CPI", color="Country",
            template="plotly_dark", title="CPI Trend Over Time", markers=True
        )
        left2.plotly_chart(fig, use_container_width=True)
    else:
        left2.warning("⚠️ No `CPI` column found in the dataset — add one to enable this chart.")

    # ---- NEW CHART 2: Parallel coordinates across all 4 metrics ----
    if "CPI" in filtered.columns:
        fig = px.parallel_coordinates(
            filtered,
            dimensions=["Population", "GDP", "Inflation", "CPI"],
            color="Inflation",
            color_continuous_scale="Turbo",
            template="plotly_dark",
            title=f"Multi-Metric Comparison ({year})"
        )
        right2.plotly_chart(fig, use_container_width=True)
    else:
        fig = px.parallel_coordinates(
            filtered,
            dimensions=["Population", "GDP", "Inflation"],
            color="Inflation",
            color_continuous_scale="Turbo",
            template="plotly_dark",
            title=f"Multi-Metric Comparison ({year})"
        )
        right2.plotly_chart(fig, use_container_width=True)

    # ---- Key Insights ----
    pop_gdp_corr = corr.loc["Population", "GDP"]
    gdp_inf_corr = corr.loc["GDP", "Inflation"]

    insight_lines = f"""
    • Population and GDP show a correlation of <b>{pop_gdp_corr:.2f}</b> among selected countries.<br>
    • GDP and Inflation show a correlation of <b>{gdp_inf_corr:.2f}</b>.<br>
    • Larger population does not always mean higher GDP — check the scatter plot for outliers.<br>
    """

    if "CPI" in corr.columns:
        cpi_inf_corr = corr.loc["CPI", "Inflation"]
        insight_lines += f"• CPI and Inflation move together with a correlation of <b>{cpi_inf_corr:.2f}</b>, as expected since CPI drives inflation calculations.<br>"

    insight_lines += "• Countries with high inflation and low GDP may signal macroeconomic instability worth investigating further."

    st.subheader("🔑 Key Insights")
    insight_box(insight_lines)



# ===== DATASET TAB =====
with tab_data:
    st.subheader("📄 Filtered Dataset")
    st.dataframe(filtered, use_container_width=True)

    csv = filtered.to_csv(index=False).encode()
    st.download_button(
        "📥 Download Filtered Data (CSV)",
        csv,
        "west_africa_data.csv",
        "text/csv"
    )

    # ---- Key Insights ----
    st.subheader("🔑 Key Insights")
    insight_box(f"""
    • Dataset covers <b>{df.Year.min()}–{df.Year.max()}</b> across <b>{df.Country.nunique()}</b> countries.<br>
    • Current filtered view: <b>{filtered.shape[0]}</b> rows, <b>{filtered.shape[1]}</b> columns.<br>
    • Use the download button to export this exact filtered slice for further analysis.
    """)

# -----------------------------------
# FOOTER
# -----------------------------------
st.markdown("---")
st.caption("""
Developed by **Olaniyan Ridwan Olasunkanmi**  
MSc Applied Statistics | Data Scientist  
Built with Streamlit • Plotly • Python
""")