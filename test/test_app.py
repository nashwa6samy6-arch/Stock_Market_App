import pandas as pd
from modules import api_handler, data_processor

def test_validate_symbol_valid():
    is_valid, msg = api_handler.validate_symbol("AAPL")
    assert is_valid == True
    assert msg == ""

def test_validate_symbol_empty():
    is_valid, msg = api_handler.validate_symbol("   ")
    assert is_valid == False
    assert "Please enter a stock symbol" in msg

def test_validate_symbol_too_long():
    is_valid, msg = api_handler.validate_symbol("ABCDEFGHIJKLMNOP")
    assert is_valid == False
    assert "too long" in msg

def test_validate_symbol_invalid_chars():
    is_valid, msg = api_handler.validate_symbol("AAPL!@#")
    assert is_valid == False
    assert "invalid characters" in msg

def test_clean_historical_data():
    data = {
        "Open": [100.0, None, 102.0],
        "High": [101.0, 105.0, 103.0],
        "Low": [99.0, 98.0, 101.0],
        "Close": [100.5, None, 102.5],
        "Volume": [1000, 2000, 1500]
    }
    df = pd.DataFrame(data, index=pd.date_range("2023-01-01", periods=3))
    
    cleaned_df = data_processor.clean_historical_data(df)
    
    assert len(cleaned_df) == 2  # One row dropped due to missing Close
    assert "Close" in cleaned_df.columns
    assert cleaned_df["Volume"].dtype == int

def test_add_indicators():
    data = {
        "Open": [100, 101, 102, 103, 104, 105, 106, 107],
        "High": [101, 102, 103, 104, 105, 106, 107, 108],
        "Low": [99, 100, 101, 102, 103, 104, 105, 106],
        "Close": [100, 101, 102, 103, 104, 105, 106, 107],
        "Volume": [1000]*8
    }
    df = pd.DataFrame(data)
    df_indicators = data_processor.add_indicators(df)
    
    assert "Daily_Change" in df_indicators.columns
    assert "Daily_Change_Pct" in df_indicators.columns
    assert "MA7" in df_indicators.columns
    assert "MA14" in df_indicators.columns
    
    # 7th element's MA7 should be calculated
    assert not pd.isna(df_indicators["MA7"].iloc[6])

def run():
    # Only here if streamlit_app still calls test_app.run()
    import streamlit as st
    st.info("Tests are implemented in `test_app.py`. Run `pytest test/test_app.py` in the terminal to execute them.")
