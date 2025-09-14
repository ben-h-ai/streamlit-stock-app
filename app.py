import pandas as pd
import streamlit as st
import yfinance as yf
import altair as alt

# Page Config
st.set_page_config(page_title="Stock Analysis")
st.title("Stock Analysis :chart_with_upwards_trend:")

# Sidebar
st.sidebar.header("Filters")
symbol = st.sidebar.text_input("Symbol", "NVDA")

# Filters
period = st.sidebar.segmented_control(label="Period", options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"], default="2y")
interval = st.sidebar.segmented_control(label="Interval", options=["1d", "1wk", "1mo"], default="1wk")
additional_price_types = st.sidebar.multiselect(label="Additional Price Types", options=["Open", "High", "Low"])

# Ticker
ticker = yf.Ticker(symbol)

# Base Price History Data Frame
price_history = ticker.history(period=period, interval=interval).reset_index()
price_history.sort_values(by="Date", ascending=False, inplace=True)

# Fixed Price Line Chart
price_history_filtered = price_history[["Date", "Close"] + additional_price_types]
price_history_filtered_melted = price_history_filtered.melt("Date", var_name="Series", value_name="Price")

# Create a selection that follows the mouse
hover = alt.selection_single(
    fields=["Date"],
    nearest=True,
    on="mouseover",
    empty="none",
    clear="mouseout"
)

# Base line chart
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

chart = (price_history_line + price_points + rule)

st.altair_chart(chart)
