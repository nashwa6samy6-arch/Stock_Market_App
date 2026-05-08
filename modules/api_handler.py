# Member 1 – Project Lead / Backend Developer
# Responsibilities:
#   - Set up Python project structure
#   - Integrate stock data API using yFinance
#   - Handle stock symbol input and validation
#   - Fetch current + historical stock data
#   - Manage error handling (invalid symbols, API failures)

import yfinance as yf
import pandas as pd
import streamlit as st

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────
PERIOD_OPTIONS = {
    "7 Days":  "7d",
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year":  "1y",
}

# ──────────────────────────────────────────────
# Validation
# ──────────────────────────────────────────────
def validate_symbol(symbol: str) -> tuple:
    """
    Basic client-side validation before hitting the API.
    Returns (is_valid: bool, error_message: str).
    """
    symbol = symbol.strip().upper()
    if not symbol:
        return False, "Please enter a stock symbol."
    if len(symbol) > 10:
        return False, f"'{symbol}' is too long to be a valid ticker symbol."
    if not symbol.replace(".", "").replace("-", "").isalnum():
        return False, f"'{symbol}' contains invalid characters. Use letters, digits, '.', or '-'."
    return True, ""


# ──────────────────────────────────────────────
# API Calls
# ──────────────────────────────────────────────
def fetch_stock_info(symbol: str):
    """
    Fetch current stock information for a given symbol.
    Returns a cleaned info dict, or None on failure.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # yfinance returns a minimal/empty dict for invalid symbols
        if not info or info.get("quoteType") is None:
            return None

        return {
            "symbol":         symbol.upper(),
            "name":           info.get("longName") or info.get("shortName") or symbol.upper(),
            "current_price":  info.get("currentPrice") or info.get("regularMarketPrice"),
            "previous_close": info.get("previousClose") or info.get("regularMarketPreviousClose"),
            "open":           info.get("open") or info.get("regularMarketOpen"),
            "day_high":       info.get("dayHigh") or info.get("regularMarketDayHigh"),
            "day_low":        info.get("dayLow") or info.get("regularMarketDayLow"),
            "volume":         info.get("volume") or info.get("regularMarketVolume"),
            "market_cap":     info.get("marketCap"),
            "currency":       info.get("currency", "USD"),
            "exchange":       info.get("exchange", ""),
            "sector":         info.get("sector", ""),
            "industry":       info.get("industry", ""),
        }
    except Exception as e:
        st.error(f"API error while fetching info for '{symbol}': {e}")
        return None


def fetch_historical_data(symbol: str, period: str = "1mo"):
    """
    Fetch OHLCV historical data for a given symbol and period.
    period options: '7d', '1mo', '3mo', '6mo', '1y'
    Returns a DataFrame (Date index, columns: Open High Low Close Volume),
    or None on failure.
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)

        if hist.empty:
            return None

        # Keep only relevant columns; strip timezone from index for clean display
        hist = hist[["Open", "High", "Low", "Close", "Volume"]].copy()
        hist.index = hist.index.tz_localize(None)
        hist.index.name = "Date"
        hist = hist.round(4)
        return hist

    except Exception as e:
        st.error(f"API error while fetching historical data for '{symbol}': {e}")
        return None


# ──────────────────────────────────────────────
# Streamlit UI Section (Member 1's portion)
# ──────────────────────────────────────────────
def run():
    st.header("📡 Stock Data — API & Input Handler")
    st.markdown("*Member 1 · Backend / API Integration*")
    st.divider()

    # ── Symbol Input ──────────────────────────
    col1, col2 = st.columns([3, 1])
    with col1:
        raw_symbol = st.text_input(
            "Enter Stock Symbol",
            placeholder="e.g. AAPL, TSLA, AMZN",
            help="Type a valid stock ticker symbol and press Enter or click Fetch.",
        )
    with col2:
        period_label = st.selectbox("Time Period", list(PERIOD_OPTIONS.keys()), index=1)

    fetch_clicked = st.button("🔍 Fetch Stock Data", type="primary", use_container_width=True)

    if not fetch_clicked:
        st.info("Enter a stock symbol above and click **Fetch Stock Data** to begin.")
        return

    # ── Validate ──────────────────────────────
    is_valid, err_msg = validate_symbol(raw_symbol)
    if not is_valid:
        st.error(f"⚠️ Invalid input: {err_msg}")
        return

    symbol = raw_symbol.strip().upper()
    period = PERIOD_OPTIONS[period_label]

    # ── Fetch from API ─────────────────────────
    with st.spinner(f"Fetching data for **{symbol}** …"):
        info = fetch_stock_info(symbol)
        hist = fetch_historical_data(symbol, period)

    # ── Check API response validity ────────────
    if info is None or hist is None:
        st.error(
            f"❌ Could not find data for **'{symbol}'**. "
            "Please check the symbol and try again."
        )
        st.markdown(
            "**Tips:**\n"
            "- Make sure the ticker is correct (e.g. `AAPL` not `Apple`).\n"
            "- Some symbols may not be available on Yahoo Finance.\n"
            "- Check your internet connection."
        )
        return

    # ── Store in session state for other members ──
    st.session_state["stock_symbol"] = symbol
    st.session_state["stock_info"]   = info
    st.session_state["stock_hist"]   = hist
    st.session_state["stock_period"] = period_label

    # ── Display current stock info ─────────────
    st.success(f"✅ Data loaded for **{info['name']} ({symbol})**")

    price      = info["current_price"]
    prev       = info["previous_close"]
    change     = (price - prev)           if (price and prev) else None
    change_pct = (change / prev * 100)    if (change and prev) else None

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(
        "Current Price",
        f"{info['currency']} {price:,.2f}" if price else "N/A",
        delta=f"{change:+.2f} ({change_pct:+.2f}%)" if change is not None else None,
    )
    m2.metric("Day High", f"{info['currency']} {info['day_high']:,.2f}" if info['day_high'] else "N/A")
    m3.metric("Day Low",  f"{info['currency']} {info['day_low']:,.2f}"  if info['day_low']  else "N/A")
    m4.metric("Volume",   f"{info['volume']:,}"                          if info['volume']   else "N/A")

    with st.expander("ℹ️ More Stock Details"):
        details = {
            "Exchange":       info["exchange"],
            "Sector":         info["sector"],
            "Industry":       info["industry"],
            "Market Cap":     f"{info['currency']} {info['market_cap']:,}" if info["market_cap"] else "N/A",
            "Open":           f"{info['currency']} {info['open']:,.2f}"    if info["open"]        else "N/A",
            "Previous Close": f"{info['currency']} {info['previous_close']:,.2f}" if prev         else "N/A",
        }
        for k, v in details.items():
            st.write(f"**{k}:** {v}")

    # ── Historical data table ──────────────────
    st.subheader(f"📊 Historical Data — {period_label}")
    st.dataframe(
        hist.style.format({
            "Open":   "{:.2f}",
            "High":   "{:.2f}",
            "Low":    "{:.2f}",
            "Close":  "{:.2f}",
            "Volume": "{:,.0f}",
        }),
        use_container_width=True,
    )
