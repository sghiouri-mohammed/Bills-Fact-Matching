import streamlit as st

from src.client.modules.home.main import main as home_main
from src.client.modules.benchmark.main import main as benchmark_main
from src.client.modules.about.main import main as about_main
from src.client.modules.pricing.main import main as pricing_main
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# export main
def main():
    # Set page config as the VERY FIRST Streamlit command
    st.set_page_config(layout="wide")

    # Initialize session state (using the function from the home module component)
    # Need to ensure AppService is available or passed if session_state.initialize needs it
    # Checking session_state.py, it seems to instantiate AppService itself if needed.
    # However, it's better practice to instantiate it once and potentially pass it around.
    # For now, we rely on the home module's session state initialization.

    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select a page", ["Home", "Benchmark", "Pricing", "About"])

    if page == "Home":
        # Call the home page rendering function
        home_main()
    # Add other pages here if needed
    elif page == "Benchmark":
        benchmark_main()
    elif page == "Pricing":
        pricing_main()
    elif page == "About":
        about_main()

if __name__ == "__main__":
    main()



