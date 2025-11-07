import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.title("Discounted Cash Flow Analysis")

st.sidebar.header("DCF Parameters")
symbol = st.sidebar.text_input("Symbol", "NVDA")
forecast_years = st.sidebar.slider(
    label="Years to forecast",
    min_value=5,
    max_value=10,
    value=10
)
expected_growth_rate = st.sidebar.number_input(
    label="Expected growth rate",
    min_value=0.0,
    max_value=1.0,
    step=0.05,
    value=0.2
)
discount_rate = st.sidebar.number_input(
    label="Discount rate (WAAC)",
    min_value=0.0,
    max_value=1.0,
    step=0.01,
    value=0.1
)
terminal_growth_rate = st.sidebar.number_input(
    label="Terminal growth rate",
    min_value=0.0,
    max_value=1.0,
    step=0.01,
    value=0.03
)

ticker = yf.Ticker(symbol)

cash_flow = ticker.cash_flow
cash_flow_items = cash_flow.loc[
    [
        "Net Income From Continuing Operations",
        "Capital Expenditure",
        "End Cash Position",
        "Free Cash Flow"
    ]
]
cash_flow_items_df = cash_flow_items.T.dropna()

st.subheader("Annual Cash Flow")
st.dataframe(
    cash_flow_items_df,
    width="content",
    column_config={
        "_index": st.column_config.DateColumn(
            label="Date",
            format="MMM YYYY"
        ),
        "Net Income From Continuing Operations": st.column_config.NumberColumn(
            format="compact"
        ),
        "Capital Expenditure": st.column_config.NumberColumn(
            format="compact"
        ),
        "End Cash Position": st.column_config.NumberColumn(
            format="compact"
        ),
        "Free Cash Flow": st.column_config.NumberColumn(
            format="compact"
        )
    }
)

quarterly_cash_flow = ticker.quarterly_cash_flow
quarterly_free_cash_flow = quarterly_cash_flow.loc["Free Cash Flow"]
quarterly_free_cash_flow_df = quarterly_free_cash_flow.T.dropna()

st.subheader("Quarterly Free Cash Flow")
st.dataframe(
    quarterly_free_cash_flow_df,
    width="content",
    column_config={
        "_index": st.column_config.DateColumn(
            label="Date",
            format="MMM YYYY"
        ),
        "Free Cash Flow": st.column_config.NumberColumn(
            format="compact"
        )
    }
)

ttm_free_cash_flow = quarterly_free_cash_flow.iloc[:4].sum()
st.metric("TTM free cash flow", f"{ttm_free_cash_flow:,.0f}", border=True, width="content")

# Free Cash Flow Forecast

forecast_df = pd.DataFrame(
    {
        "year": np.arange(1, forecast_years + 1)
    }
).set_index("year")

forecast_df["projected_free_cash_flow"] = ttm_free_cash_flow * (1 + expected_growth_rate) ** forecast_df.index
forecast_df["discount_factor"] = 1 / (1 + discount_rate) ** forecast_df.index
forecast_df["discounted_free_cash_flow"] = forecast_df["projected_free_cash_flow"] * forecast_df["discount_factor"]

st.subheader("Free Cash Flow Forecast")
st.dataframe(
    forecast_df,
    width="content",
    column_config={
        "_index": st.column_config.NumberColumn(
            label="Year",
            format="plain"
        ),
        "projected_free_cash_flow": st.column_config.NumberColumn(
            label="Projected Free Cash Flow",
            format="compact"
        ),
        "discount_factor": st.column_config.NumberColumn(
            label="Discount Factor",
            format="compact"
        ),
        "discounted_free_cash_flow": st.column_config.NumberColumn(
            label="Discounted Free Cash Flow",
            format="compact"
        )
    }
)

# Terminal Value and Enterprise Value

st.subheader("Enterprise Value")
free_cash_flow_n = forecast_df["projected_free_cash_flow"].iloc[-1]
terminal_value = (free_cash_flow_n * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
st.text(f"Terminal value: {terminal_value:,.0f}")
discounted_terminal_value = terminal_value / (1 + discount_rate) ** forecast_years
st.text(f"Discounted terminal value: {discounted_terminal_value:,.0f}")
enterprise_value = forecast_df["discounted_free_cash_flow"].sum() + discounted_terminal_value
st.metric("Enterprise value", f"{enterprise_value:,.0f}", border=True, width="content")

st.subheader("Equity Value")
quarterly_balance_sheet = ticker.quarterly_balance_sheet
cash = quarterly_balance_sheet.loc["Cash And Cash Equivalents"].iloc[0]
total_debt = quarterly_balance_sheet.loc["Total Debt"].iloc[0]
equity_value = enterprise_value - total_debt + cash

st.text(f"Total debt: {total_debt:,.0f}")
st.text(f"Cash: {cash:,.0f}")
st.metric("Equity value", f"{equity_value:,.0f}", border=True, width="content")

# Intrinsic Value

st.subheader("Intrinsic Value")
shares_outstanding = ticker.fast_info.shares
st.text(f"Shares outstanding: {shares_outstanding:,.0f}")

intrinsic_value_per_share = equity_value / shares_outstanding
last_price = ticker.fast_info.last_price
valuation_delta = intrinsic_value_per_share - last_price
relative_valuation = valuation_delta / last_price

col1, col2, col3 = st.columns(3)
col1.metric("Intrinsic value per share", f"{intrinsic_value_per_share:,.2f}", border=True)
col2.metric("Last price", f"{last_price:,.2f}", border=True)
col3.metric("Relative opportunity", f"{relative_valuation:.2%}", border=True)
