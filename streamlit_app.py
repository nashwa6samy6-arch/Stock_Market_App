from modules import ui
import streamlit as st

# Member 4 - Unified Streamlit UI
st.set_page_config(
    page_title="Stock Market App",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

ui.run()
