import pandas as pd
import requests
import plotly.graph_objects as go
import streamlit as st

COINGECKO_API_KEY = "CG-pE5tyRAPp51kPXNKYNAU9e1a"


def fetch_crypto(ticker: str, additional_ticker: str = None, timeframe: str = "1m"):
    if ticker == "":
        st.error("Please enter a ticker")
        return
    else:
        ticker = ticker.lower()

    if timeframe == "1w":
        days = 7
    elif timeframe == "1m":
        days = 30
    elif timeframe == "3m":
        days = 90
    elif timeframe == "1y":
        days = 365

    url = f"https://api.coingecko.com/api/v3/coins/{ticker}/market_chart"
    response = requests.get(url, params={"vs_currency": "usd", "days": days})

    if response.status_code == 429:
        st.error(response.json()["status"]["error_message"])
    elif "prices" not in response.json():
        st.error("Invalid ticker")
        return
    else:
        st.session_state["df_crypto"] = pd.DataFrame(response.json()["prices"], columns=["date", "close"])
        st.session_state["df_crypto"]["date"] = pd.to_datetime(st.session_state["df_crypto"]["date"], unit="ms")

    if additional_ticker:
        url = f"https://api.coingecko.com/api/v3/coins/{additional_ticker}/market_chart"
        response = requests.get(url, params={"vs_currency": "usd", "days": days})

        if response.status_code == 429:
            st.error(response.json()["status"]["error_message"])
        elif "prices" not in response.json():
            st.error("Invalid ticker")
            return
        else:
            st.session_state["df_crypto_2"] = pd.DataFrame(response.json()["prices"], columns=["date", "close"])


def display_one_crypto():
    df_crypto = st.session_state["df_crypto"]

    max_price_date = df_crypto["close"].idxmax()
    max_price = st.session_state["df_crypto"]["close"].max()
    min_price_date = df_crypto["close"].idxmin()
    min_price = st.session_state["df_crypto"]["close"].min()

    fig = go.Figure(data=go.Scatter(x=df_crypto["date"], y=df_crypto["close"]))
    fig.update_yaxes(range=[min_price * 0.99, max_price * 1.01])

    if df_crypto["date"].nunique() < 10:
        fig.update_xaxes(nticks=len(df_crypto["date"].unique()))

    st.plotly_chart(fig)

    st.write(f"Highest: **{format(max_price, '.2f')}** on {str(df_crypto['date'][max_price_date]).split('.')[0]}")
    st.write(f"Lowest: **{format(min_price, '.2f')}** on {str(df_crypto['date'][min_price_date]).split('.')[0]}")


def display_two_cryptos(ticker1: str, ticker2: str):
    df_crypto = st.session_state["df_crypto"]
    df_crypto_2 = st.session_state["df_crypto_2"]

    fig = go.Figure()

    if df_crypto["date"].nunique() < 10:
        fig.update_xaxes(nticks=len(df_crypto["date"].unique()))

    # Add the first trace
    fig.add_trace(go.Scatter(x=df_crypto["date"], y=df_crypto["close"], mode="lines", name=ticker1))

    # Add the second trace
    fig.add_trace(go.Scatter(x=df_crypto_2["date"], y=df_crypto_2["close"], mode="lines", name=ticker2))

    st.plotly_chart(fig)


def streamlit_app():
    st.set_page_config(page_title="Cryptocurrency Chart")
    st.title("Cryptocurrency Chart")

    compare_crypto = st.toggle("Compare cryptocurrencies")
    timeframe = st.radio(
        "Timeline (CoinGecko API allows maximum of 1 year of historical data for free account)",
        ["1w", "1m", "3m", "1y"],
    )

    if not compare_crypto:
        ticker = st.text_input("Enter the cryptocurrency ticker", "bitcoin")
        st.button(
            "Search",
            on_click=fetch_crypto,
            args=(ticker, None, timeframe),
            type="primary",
        )

        if "df_crypto" in st.session_state:
            display_one_crypto()
    else:
        st.write("Enter the tickers of the cryptocurrencies you want to compare")
        ticker1 = st.text_input("Enter the first cryptocurrency ticker", "bitcoin")
        ticker2 = st.text_input("Enter the second cryptocurrency ticker", "ethereum")
        st.button(
            "Search",
            on_click=fetch_crypto,
            args=(ticker1, ticker2, timeframe),
            type="primary",
        )

        if "df_crypto" in st.session_state and "df_crypto_2" in st.session_state:
            display_two_cryptos(ticker1, ticker2)


streamlit_app()
