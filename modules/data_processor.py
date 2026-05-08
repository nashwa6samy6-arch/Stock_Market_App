# Member 2 – Data Processing & Analysis

import pandas as pd
import streamlit as st


def clean_historical_data(hist: pd.DataFrame) -> pd.DataFrame:
    df = hist.copy()
    df = df.dropna(subset=["Close"])
    df = df.sort_index(ascending=True)
    df[["Open", "High", "Low", "Close"]] = df[["Open", "High", "Low", "Close"]].astype(float)
    df["Volume"] = df["Volume"].astype(int)
    return df


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Daily_Change"]     = df["Close"].diff()
    df["Daily_Change_Pct"] = df["Close"].pct_change() * 100
    df["MA7"]  = df["Close"].rolling(window=7).mean()
    df["MA14"] = df["Close"].rolling(window=14).mean()
    df = df.round(4)
    return df


def get_summary_stats(df: pd.DataFrame) -> dict:
    close = df["Close"]
    return {
        "Highest Close":    round(close.max(), 2),
        "Lowest Close":     round(close.min(), 2),
        "Average Close":    round(close.mean(), 2),
        "Total Volume":     int(df["Volume"].sum()),
        "Best Day Change":  round(df["Daily_Change_Pct"].max(), 2),
        "Worst Day Change": round(df["Daily_Change_Pct"].min(), 2),
        "Volatility (Std)": round(close.std(), 2),
    }


def run():
    st.header("🧹 Data Processing & Analysis")
    st.markdown("*Member 2 · Data Handling & Indicators*")
    st.divider()

    if "stock_hist" not in st.session_state or "stock_info" not in st.session_state:
        st.info("⬆️ Please fetch a stock using the section above first.")
        return

    hist   = st.session_state["stock_hist"]
    info   = st.session_state["stock_info"]
    symbol = st.session_state.get("stock_symbol", "")
    period = st.session_state.get("stock_period", "")

    df = clean_historical_data(hist)
    df = add_indicators(df)

    # Save for Member 3 (visualizer uses these keys)
    st.session_state["processed_df"] = df
    st.session_state["stock_df"]     = df
    st.session_state["symbol"]       = symbol

    # Summary stats
    st.subheader(f"📈 Summary Statistics — {symbol} ({period})")
    stats = get_summary_stats(df)

    col1, col2, col3 = st.columns(3)
    stat_items = list(stats.items())

    for i, (label, value) in enumerate(stat_items):
        col = [col1, col2, col3][i % 3]
        if "Change" in label:
            col.metric(label, f"{value}%")
        elif "Volume" in label:
            col.metric(label, f"{value:,}")
        else:
            col.metric(label, f"{info['currency']} {value:,}")

    # Processed data table
    st.subheader("🗂️ Processed Data with Indicators")
    st.caption("MA7 = 7-day Moving Average | MA14 = 14-day Moving Average")

    display_df = df.copy()
    display_df.index = display_df.index.strftime("%Y-%m-%d")

    st.dataframe(
        display_df.style.format({
            "Open":             "{:.2f}",
            "High":             "{:.2f}",
            "Low":              "{:.2f}",
            "Close":            "{:.2f}",
            "Volume":           "{:,.0f}",
            "Daily_Change":     "{:+.2f}",
            "Daily_Change_Pct": "{:+.2f}%",
            "MA7":              "{:.2f}",
            "MA14":             "{:.2f}",
        }, na_rep="—"),
        use_container_width=True,
    )