import streamlit as st
from fredapi import Fred
import pandas as pd
import plotly.express as px

# FRED API Setup
fred = Fred(api_key="77750e28c1fc3822266cbf14fffb80bf")

# LINK TO WEBSITE
# https://f2partners-daily-market-dashboard.streamlit.app/

# App Title
st.title("Flynn Financial Daily Market Dashboard")

# ----------------------------
#  Summary Cards Section
# ----------------------------
st.subheader(" Key Rates Snapshot")

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
    except Exception as e:
        cols[i].write(f"{label} data unavailable.")

# ----------------------------
# Show All Charts
# ----------------------------
st.subheader(" Market Series Charts")

# Select how many years of data to show
years = st.slider("Select number of years of data to show:", 1, 10, 5)

all_series = {
    "Federal Funds Rate": "FEDFUNDS",
    "10Y Treasury Yield": "GS10",
    "30Y Mortgage Rate": "MORTGAGE30US"
}

for name, code in all_series.items():
    try:
        data = fred.get_series(code).dropna()
        data = data[data.index > pd.Timestamp.today() - pd.DateOffset(years=years)]

        fig = px.line(
            x=data.index,
            y=data.values,
            title=f"{name} - Last {years} Years",
            labels={'x': 'Date', 'y': 'Percent'}
        )
        fig.update_traces(mode="lines+markers")
        fig.update_layout(hovermode="x unified")

        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not load chart for {name}")
