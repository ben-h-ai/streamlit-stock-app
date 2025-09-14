import streamlit as st
import yfinance as yf
import pandas as pd

st.title("📈 Stock Analysis App")

ticker = st.text_input("Enter Stock Ticker", "AAPL")
if ticker:
    data = yf.download(ticker, period="5y", interval="1d")
    st.line_chart(data["Close"])