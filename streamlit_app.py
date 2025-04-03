import os
import sys
import streamlit as st

# Gestion des chemins d'importation
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Configurations Streamlit
st.set_page_config(
    page_title="Bills-Fact-Matching",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    # Importation des modules de l'application
    from src.client.modules.home.main import main as home_main
    from src.client.modules.benchmark.main import main as benchmark_main
    from src.client.modules.about.main import main as about_main
    from src.client.modules.pricing.main import main as pricing_main
    import logging

    # Configuration des logs
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.info("Démarrage de l'application")

    # Interface de navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select a page", ["Home", "Benchmark", "Pricing", "About"])

    # Affichage de la page sélectionnée
    if page == "Home":
        home_main()
    elif page == "Benchmark":
        benchmark_main()
    elif page == "Pricing":
        pricing_main()
    elif page == "About":
        about_main()

except Exception as e:
    st.error(f"Erreur lors du chargement de l'application: {str(e)}")
    st.error("Détails techniques:")
    import traceback
    st.code(traceback.format_exc())
    
    # Affichage des informations de débogage
    st.subheader("Information de débogage:")
    st.write(f"Python version: {sys.version}")
    st.write(f"Streamlit version: {st.__version__}")
    st.write(f"Chemin système: {sys.path}")
    st.write("Fichiers dans le répertoire courant:")
    try:
        files = os.listdir('.')
        st.write(files)
    except Exception as e:
        st.write(f"Erreur lors de la lecture des fichiers: {e}") 