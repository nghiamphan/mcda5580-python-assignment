import pandas as pd
import requests
import plotly.graph_objects as go
import streamlit as st

IEX_CLOUD_API_KEY = "pk_86911959950f414f83425281189cc6f6"


def fetch_stock(ticker: str, additional_ticker: str = None, timeframe: str = "1m"):
    url = f"https://cloud.iexapis.com/stable/stock/{ticker}/chart/{timeframe}"
    response = requests.get(url, params={"token": IEX_CLOUD_API_KEY})
    st.session_state["df_stock"] = pd.DataFrame(response.json())

    if additional_ticker:
        url = f"https://cloud.iexapis.com/stable/stock/{additional_ticker}/chart/{timeframe}"
        response = requests.get(url, params={"token": IEX_CLOUD_API_KEY})
        st.session_state["df_stock_2"] = pd.DataFrame(response.json())


def display_one_stock():
    df_stock = st.session_state["df_stock"]

    max_price_date = df_stock["close"].idxmax()
    max_price = st.session_state["df_stock"]["close"].max()
    min_price_date = df_stock["close"].idxmin()
    min_price = st.session_state["df_stock"]["close"].min()

    fig = go.Figure(data=go.Scatter(x=df_stock["date"], y=df_stock["close"]))
    fig.update_yaxes(range=[min_price * 0.99, max_price * 1.01])

    if df_stock["date"].nunique() < 10:
        fig.update_xaxes(nticks=len(df_stock["date"].unique()))

    st.plotly_chart(fig)

    st.write(f"Highest: **{max_price}** on {df_stock['date'][max_price_date]}")
    st.write(f"Lowest: **{min_price}** on {df_stock['date'][min_price_date]}")


def display_two_stocks(ticker1: str, ticker2: str):
    df_stock = st.session_state["df_stock"]
    df_stock_2 = st.session_state["df_stock_2"]

    fig = go.Figure()

    if df_stock["date"].nunique() < 10:
        fig.update_xaxes(nticks=len(df_stock["date"].unique()))

    # Add the first trace
    fig.add_trace(go.Scatter(x=df_stock["date"], y=df_stock["close"], mode="lines", name=ticker1))

    # Add the second trace
    fig.add_trace(go.Scatter(x=df_stock_2["date"], y=df_stock_2["close"], mode="lines", name=ticker2))

    st.plotly_chart(fig)


compare_stock = st.toggle("Compare stocks")
timeframe = st.radio("Timeline", ["1w", "1m", "1y", "5y"])

if not compare_stock:
    ticker = st.text_input("Enter a stock ticker", "AAPL")
    st.button(
        "Search",
        on_click=fetch_stock,
        args=(ticker, None, timeframe),
        type="primary",
    )

    if "df_stock" in st.session_state:
        display_one_stock()
else:
    st.write("Compare stocks")
    ticker1 = st.text_input("Enter a stock ticker", "AAPL")
    ticker2 = st.text_input("Enter a stock ticker", "GOOGL")
    st.button(
        "Search",
        on_click=fetch_stock,
        args=(ticker1, ticker2, timeframe),
        type="primary",
    )

    if "df_stock" in st.session_state and "df_stock_2" in st.session_state:
        display_two_stocks(ticker1, ticker2)
