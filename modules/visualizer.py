# member3
# modules/visualizer.py
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def plot_price_trend(df: pd.DataFrame, symbol: str):
    """Line chart showing closing price over time."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Close"],
        mode="lines+markers",
        name="Close Price",
        line=dict(color="#00C8FF", width=2),
        marker=dict(size=4)
    ))
    fig.update_layout(
        title=f"📈 {symbol} — Price Trend",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_dark",
        hovermode="x unified"
    )
    return fig

def plot_candlestick(df: pd.DataFrame, symbol: str):
    """Candlestick chart for OHLC data."""
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name=symbol
    )])
    fig.update_layout(
        title=f"🕯️ {symbol} — Candlestick Chart",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_dark",
        xaxis_rangeslider_visible=False
    )
    return fig

def plot_volume(df: pd.DataFrame, symbol: str):
    """Bar chart for trading volume."""
    fig = px.bar(
        df,
        x=df.index,
        y="Volume",
        title=f"📊 {symbol} — Trading Volume",
        labels={"x": "Date", "Volume": "Volume"},
        color_discrete_sequence=["#7B61FF"]
    )
    fig.update_layout(template="plotly_dark")
    return fig

def plot_moving_average(df: pd.DataFrame, symbol: str, window: int = 7):
    """Line chart with moving average overlay."""
    df = df.copy()
    df[f"MA{window}"] = df["Close"].rolling(window=window).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"],
        mode="lines", name="Close Price",
        line=dict(color="#00C8FF")
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df[f"MA{window}"],
        mode="lines", name=f"{window}-Day MA",
        line=dict(color="#FF6B6B", dash="dash")
    ))
    fig.update_layout(
        title=f"📉 {symbol} — Price with {window}-Day Moving Average",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_dark",
        hovermode="x unified"
    )
    return fig

def run():
    """Called by streamlit_app.py — renders all charts in the Streamlit UI."""
    st.header("📊 Stock Visualizations")

    # Get shared data from session state (set by Member 1 & 2)
    df = st.session_state.get("stock_df", None)
    symbol = st.session_state.get("symbol", "")

    if df is None or df.empty:
        st.info("Enter a stock symbol above to see charts.")
        return

    # Chart type selector
    chart_type = st.selectbox(
        "Select Chart Type",
        ["Price Trend", "Candlestick", "Volume", "Moving Average"]
    )

    if chart_type == "Price Trend":
        fig = plot_price_trend(df, symbol)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Candlestick":
        fig = plot_candlestick(df, symbol)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Volume":
        fig = plot_volume(df, symbol)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Moving Average":
        window = st.slider("Moving Average Window (days)", min_value=3, max_value=30, value=7)
        fig = plot_moving_average(df, symbol, window)
        st.plotly_chart(fig, use_container_width=True)
