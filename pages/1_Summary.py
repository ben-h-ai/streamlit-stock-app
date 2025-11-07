import pandas as pd
import streamlit as st
import yfinance as yf
import altair as alt

# Page Config
# st.set_page_config(page_title="Stock Analysis", layout="wide")
st.title("Summary")

# Sidebar
st.sidebar.header("Filters")
symbol = st.sidebar.text_input("Symbol", "NVDA")

# Filters
period = st.sidebar.segmented_control(label="Period", options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"], default="1y")
interval = st.sidebar.segmented_control(label="Interval", options=["1d", "1wk", "1mo"], default="1d")
additional_price_types = st.sidebar.multiselect(label="Additional Price Types", options=["Open", "High", "Low"])

# Ticker
ticker = yf.Ticker(symbol)

# Get company info
info = ticker.info

symbol_display = info.get("symbol")
long_name = info.get("longName")
sector = info.get("sector", "Sector not available")
industry = info.get("industry", "Industry not available")
long_business_summary = info.get("longBusinessSummary", "No description available")

# Get price data
currency = info.get("currency")
last_price = ticker.fast_info.last_price
previous_close = ticker.fast_info.previous_close
day_change = last_price - previous_close
day_percent_change = day_change / previous_close
market_cap = ticker.fast_info.market_cap

# --- Company Overview Section ---
st.header(f"{long_name} ({symbol_display})")

# Business description
col1, col2 = st.columns(2)
col1.metric("Sector", sector)
col2.metric("Industry", industry)

with st.expander("Business Description:"):
    st.write(long_business_summary)

# Key metrics
col3, col4, col5 = st.columns(3)

col3.metric("Last Price", f"{currency} {last_price:,.2f}")
col4.metric("Percent Change", f"{day_percent_change:.1%}")
col5.metric("Market Cap", f"{currency} {market_cap / 1e9:,.1f} B")

# --- Price Analysis ---

# Base Price History Data Frame
price_history = ticker.history(period=period, interval=interval).reset_index()
price_history.sort_values(by="Date", ascending=False, inplace=True)

# Fixed Price Line Chart
price_history_filtered = price_history[["Date", "Close"] + additional_price_types]
price_history_filtered_melted = price_history_filtered.melt("Date", var_name="Series", value_name="Price")

# Create a selection that follows the mouse
hover = alt.selection_point(
    fields=["Date"],
    nearest=True,
    on="mouseover",
    empty="none",
    clear="mouseout"
)

# Baseline chart
price_history_line = alt.Chart(price_history_filtered_melted).mark_line().encode(
    x=alt.X(field="Date", type="temporal", title=None),
    y=alt.Y(field="Price", type="quantitative", scale=alt.Scale(zero=False)),
    color=alt.Color(field="Series", type="nominal", title="Price Type"),
    tooltip=[
        alt.Tooltip(field="Date", type="temporal"),
        alt.Tooltip(field="Series", type="nominal", title="Price Type"),
        alt.Tooltip(field="Price", type="quantitative", format=".2f")
    ]
)

# Points that show only on hover
price_points = price_history_line.mark_point().encode(
    opacity=alt.condition(hover, alt.value(1), alt.value(0))
).add_params(hover)

# # Text labels near the points
# text = price_history_line.mark_text(align="left", dx=5, dy=-5).encode(
#     text=alt.condition(
#         hover,
#         alt.Text(field="Price", type="quantitative", format=".2f"),
#         alt.value("")
#     )
# )

# Vertical rule that moves with the cursor
rule = alt.Chart(price_history_filtered_melted).mark_rule(color="gray").encode(
    x=alt.X(field="Date", type="temporal")
).transform_filter(hover)

st.divider()
st.header("Price Analysis")
chart = (price_history_line + price_points + rule)

st.altair_chart(chart)

# --- Financials ---

st.divider()
st.header("Financials")

financials = ticker.financials

# Income statement

income_statement = ticker.income_stmt

financial_metrics = ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"]
financial_metric = st.selectbox(label="Financial Metric", options=financial_metrics, index=0, accept_new_options=False)

# Income statement
financial_metric_data = income_statement.loc[financial_metric]
# st.subheader(f"{financial_metric}")

df_financial_metric = pd.DataFrame({
    "date": financial_metric_data.index,
    "year": financial_metric_data.index.year,
    financial_metric: financial_metric_data.values
}).reset_index(drop=True)

financial_metric_chart = (
    alt.Chart(df_financial_metric)
    .mark_bar()
    .encode(
        # x=alt.X(field="date", type="temporal", timeUnit="year", title="Year"),
        x=alt.X(field="year", type="ordinal", title="Year", axis=alt.Axis(labelAngle=0)),
        y=alt.Y(field=financial_metric, type="quantitative", title=financial_metric),
        tooltip=[alt.Tooltip(field="year", type="ordinal", title="Year"),
                 alt.Tooltip(field=financial_metric, format=",.0f", title=financial_metric)]
    )
)

# theme_base = st.get_option("theme.base")
# label_colour = "black" if theme_base == "light" else "white"
#
# financial_metric_chart_text = (
#     alt.Chart(df_financial_metric)
#     .mark_text(dy=-10, color=label_colour)
#     .encode(
#         # x=alt.X(field="date", type="ordinal", timeUnit="year", title="Year"),
#         x=alt.X(field="year", type="ordinal", title="Year", axis=alt.Axis(labelAngle=0)),
#         y=alt.Y(field=financial_metric, type="quantitative", title=financial_metric),
#         text=alt.Text(field=financial_metric, type="quantitative", format=",.0f")
#     )
# )

st.altair_chart(financial_metric_chart)
