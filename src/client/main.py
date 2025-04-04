import streamlit as st

from src.client.modules.home.main import main as home_main
from src.client.modules.benchmark.main import main as benchmark_main
from src.client.modules.about.main import main as about_main
from src.client.modules.pricing.main import main as pricing_main
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Set page config as the VERY FIRST Streamlit command
    st.set_page_config(layout="wide")

    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "Home"

    # Sidebar navigation
    st.sidebar.title("Navigation")
    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    # Navigation buttons
    col1, col2, col3 = st.sidebar.columns([1, 6, 1])
    with col2:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "Home"
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("📊 Benchmark", use_container_width=True):
            st.session_state.page = "Benchmark"
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("💰 Pricing", use_container_width=True):
            st.session_state.page = "Pricing"
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("ℹ️ About", use_container_width=True):
            st.session_state.page = "About"

    # Display the selected page
    if st.session_state.page == "Home":
        home_main()
    elif st.session_state.page == "Benchmark":
        benchmark_main()
    elif st.session_state.page == "Pricing":
        pricing_main()
    elif st.session_state.page == "About":
        about_main()

if __name__ == "__main__":
    main()



