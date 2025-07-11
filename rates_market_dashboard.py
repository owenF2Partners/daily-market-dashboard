import streamlit as st
from fredapi import Fred
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# https://f2partners-rates-daily-market-dashboard.streamlit.app/

# FRED API Setup
fred = Fred(api_key="77750e28c1fc3822266cbf14fffb80bf")

# App Title
st.title("Flynn Financial Rates Daily Market Dashboard")

# ----------------------------
# Summary Cards Section
# ----------------------------
st.subheader("Key Rates Snapshot")

summary_series = {
    "Fed Funds": "FEDFUNDS",
    "UST 3M": "DGS3MO",
    "UST 1Y": "DGS1",
    "UST 10Y": "DGS10",
    "UST 30Y": "DGS30",
    "30Y Mortgage": "MORTGAGE30US"
}

cols = st.columns(len(summary_series))

for i, (label, code) in enumerate(summary_series.items()):
    try:
        ts = fred.get_series(code).dropna()
        latest_date = ts.index[-1].strftime("%Y-%m-%d")
        latest_value = round(ts.iloc[-1], 2)
        prev_value = round(ts.iloc[-2], 2)
        delta = round(latest_value - prev_value, 2)
        cols[i].metric(label, f"{latest_value}%", f"{delta:+}%", help=f"As of {latest_date}")
    except Exception:
        cols[i].write(f"{label} data unavailable.")

# ----------------------------
# Market Series Charts Section
# ----------------------------
st.subheader("Market Series Charts")

# Select history for years shown
years = st.selectbox(
    "Select number of years of data to show:",
    options=[1, 5, 10],
    index=0  # default to 1
)

# Define all chart series
all_series = {
    "Federal Funds Rate": "FEDFUNDS",
    "10Y Treasury Yield": "DGS10",
    "30Y Mortgage Rate": "MORTGAGE30US",
    "UST 1Y": "DGS1",
    "UST 3M": "DGS3MO",
    "UST 30Y": "DGS30",
    "UST 10Y - 3M": "T10Y3M",
    "10 Year Breakeven Inflation Rate": "T10YIE",
    "5-Year, 5-Year Forward Inflation Expectation Rate": "T5YIFR",
    "Moody's Seasoned Aaa Corporate Bond Yield": "DAAA",
    "Moody's Seasoned Baa Corporate Bond Yield": "DBAA",
    "ICE BofA US High Yield Index Effective Yield": "BAMLH0A0HYM2EY"
}

# Convert to list for index-based looping
series_list = list(all_series.items())

# Display 2 charts per row
for i in range(0, len(series_list), 2):
    cols = st.columns([10, 10])

    for j in range(2):
        if i + j < len(series_list):
            name, code = series_list[i + j]

            try:
                data = fred.get_series(code).dropna()
                data = data[data.index > pd.Timestamp.today() - pd.DateOffset(years=years)]
                latest_date = data.index[-1].strftime("%B %d, %Y")

                fig = px.line(
                    x=data.index,
                    y=data.values,
                    title=f"{name} - Last {years} Years",
                    labels={'x': 'Date', 'y': 'Percent'}
                )
                fig.update_traces(mode="lines+markers")
                fig.update_layout(hovermode="x unified")

                cols[j].plotly_chart(fig, use_container_width=True)
                cols[j].caption(f"Latest data as of: {latest_date}")
            except Exception:
                cols[j].warning(f"Could not load chart for {name}")
