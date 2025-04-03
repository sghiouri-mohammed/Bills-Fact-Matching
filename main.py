import sys
import os
import streamlit as st

# Récupérer le répertoire courant
current_dir = os.path.dirname(os.path.abspath(__file__))

# L'ajouter au chemin Python pour permettre les importations relatives
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
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
    else:
        main()  # Pour Streamlit Cloud, exécuter même si non exécuté comme script principal

except Exception as e:
    st.error(f"Erreur lors du chargement de l'application: {str(e)}")
    st.error("Détails techniques:")
    import traceback
    st.code(traceback.format_exc())