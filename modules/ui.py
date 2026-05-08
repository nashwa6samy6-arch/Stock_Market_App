import streamlit as st
import pandas as pd
from modules import api_handler, data_processor, visualizer

def inject_custom_css():
    st.markdown("""
        <style>
        /* Vibrant, clean styling for metrics with glassmorphism and hover effects */
        [data-testid="stMetric"] {
            background: #ffffff;
            padding: 24px 22px;
            border-radius: 20px;
            border: 1px solid rgba(0, 0, 0, 0.08);
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.06);
            transition: transform 0.25s ease, box-shadow 0.25s ease;
            min-height: 140px;
        }
        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 16px 32px rgba(0, 0, 0, 0.1);
            border-color: rgba(0, 0, 0, 0.12);
        }
        [data-testid="stMetricValue"] {
            color: #111111 !important;
            font-size: 2rem !important;
            font-weight: 800;
            letter-spacing: 0.02em;
            line-height: 1.1;
        }
        [data-testid="stMetricDelta"] {
            color: #2c7a7b !important;
            font-size: 1rem !important;
            font-weight: 700;
        }
        [data-testid="stMetricLabel"] {
            color: #4a4a4a !important;
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)


def format_large_number(value, currency=""):
    if value is None:
        return "N/A"
    abs_value = abs(value)
    suffix = ""
    if abs_value >= 1_000_000_000_000:
        value = value / 1_000_000_000_000
        suffix = "T"
    elif abs_value >= 1_000_000_000:
        value = value / 1_000_000_000
        suffix = "B"
    elif abs_value >= 1_000_000:
        value = value / 1_000_000
        suffix = "M"
    elif abs_value >= 1_000:
        value = value / 1_000
        suffix = "K"
    formatted = f"{value:,.2f}" if suffix else f"{int(value):,}"
    return f"{currency} {formatted}{suffix}"


def format_price(value, currency=""):
    if value is None:
        return "N/A"
    return f"{currency} {value:,.2f}"


def run():
    inject_custom_css()
    
    st.sidebar.title("📈 Stock Settings")
    st.sidebar.markdown("Configure your stock parameters here.")
    
    symbol = st.sidebar.text_input("Enter Stock Symbol", value="AAPL", help="e.g. AAPL, TSLA, AMZN")
    period_label = st.sidebar.selectbox("Time Period", list(api_handler.PERIOD_OPTIONS.keys()), index=1)
    
    if st.sidebar.button("Fetch Data", type="primary", use_container_width=True):
        is_valid, err_msg = api_handler.validate_symbol(symbol)
        if not is_valid:
            st.sidebar.error(f"⚠️ {err_msg}")
            return
            
        with st.spinner(f"Fetching data for {symbol.upper()}..."):
            period = api_handler.PERIOD_OPTIONS[period_label]
            info = api_handler.fetch_stock_info(symbol)
            hist = api_handler.fetch_historical_data(symbol, period)
            
            if info is None or hist is None:
                st.sidebar.error(f"❌ Could not find data for '{symbol}'.")
                return
                
            st.session_state["symbol"] = symbol.upper()
            st.session_state["info"] = info
            st.session_state["hist"] = hist
            st.session_state["period_label"] = period_label
            
            # Process data
            df = data_processor.clean_historical_data(hist)
            df = data_processor.add_indicators(df)
            st.session_state["stock_df"] = df
    
    if "info" in st.session_state:
        info = st.session_state["info"]
        df = st.session_state["stock_df"]
        current_symbol = st.session_state["symbol"]
        current_period = st.session_state["period_label"]
        
        st.title(f"{info['name']} ({info['symbol']})")
        st.markdown(f"**Sector:** {info['sector']} | **Industry:** {info['industry']} | **Exchange:** {info['exchange']}")
        
        # Key Metrics
        m1, m2, m3, m4 = st.columns(4)
        price = info["current_price"]
        prev = info["previous_close"]
        change = (price - prev) if (price and prev) else None
        change_pct = (change / prev * 100) if (change and prev) else None
        
        m1.metric(
            "Current Price",
            format_price(price, info['currency']),
            f"{change:+.2f} ({change_pct:+.2f}%)" if change is not None else None,
        )
        m2.metric("Market Cap", format_large_number(info['market_cap'], info['currency']))
        m3.metric("Day High", format_price(info['day_high'], info['currency']))
        m4.metric("Volume", format_large_number(info['volume']))
        
        st.divider()
        
        # Tabs
        tab1, tab2, tab3 = st.tabs(["📊 Charts", "📉 Historical Data", "ℹ️ Company Info"])
        
        with tab1:
            col_chart, col_options = st.columns([3, 1])
            with col_options:
                st.subheader("Chart Options")
                chart_type = st.radio("Select Chart Type", ["Price Trend", "Candlestick", "Volume", "Moving Average"])
                if chart_type == "Moving Average":
                    window = st.slider("MA Window (Days)", 3, 30, 7)
            
            with col_chart:
                if chart_type == "Candlestick":
                    st.plotly_chart(visualizer.plot_candlestick(df, current_symbol), use_container_width=True)
                elif chart_type == "Price Trend":
                    st.plotly_chart(visualizer.plot_price_trend(df, current_symbol), use_container_width=True)
                elif chart_type == "Volume":
                    st.plotly_chart(visualizer.plot_volume(df, current_symbol), use_container_width=True)
                elif chart_type == "Moving Average":
                    st.plotly_chart(visualizer.plot_moving_average(df, current_symbol, window), use_container_width=True)
                    
        with tab2:
            st.subheader(f"Data & Indicators — {current_period}")
            stats = data_processor.get_summary_stats(df)
            
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Highest Close", f"{info['currency']} {stats['Highest Close']}")
            s2.metric("Lowest Close", f"{info['currency']} {stats['Lowest Close']}")
            s3.metric("Average Close", f"{info['currency']} {stats['Average Close']}")
            s4.metric("Volatility (Std)", stats['Volatility (Std)'])
            
            st.markdown("##### Detailed DataFrame")
            display_df = df.copy()
            display_df.index = display_df.index.strftime("%Y-%m-%d")
            st.dataframe(
                display_df.style.format({
                    "Open": "{:.2f}", "High": "{:.2f}", "Low": "{:.2f}", "Close": "{:.2f}",
                    "Volume": "{:,.0f}", "Daily_Change": "{:+.2f}", "Daily_Change_Pct": "{:+.2f}%",
                    "MA7": "{:.2f}", "MA14": "{:.2f}",
                }, na_rep="—"),
                use_container_width=True
            )
            
        with tab3:
            st.subheader("Company Details")
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Symbol:** {info['symbol']}")
                st.write(f"**Name:** {info['name']}")
                st.write(f"**Sector:** {info['sector']}")
                st.write(f"**Industry:** {info['industry']}")
            with c2:
                st.write(f"**Currency:** {info['currency']}")
                st.write(f"**Market Cap:** {info['currency']} {info['market_cap']:,}" if info['market_cap'] else "**Market Cap:** N/A")
                st.write(f"**Previous Close:** {info['currency']} {info['previous_close']:,.2f}" if info['previous_close'] else "**Previous Close:** N/A")
                st.write(f"**Open:** {info['currency']} {info['open']:,.2f}" if info['open'] else "**Open:** N/A")
    else:
        st.info("👈 Please enter a stock symbol in the sidebar and click 'Fetch Data' to view the dashboard.")
