import streamlit as st

from src.client.modules.home.state import initialize_session_state
from src.client.modules.home.components import file_upload, control_buttons, processing_logic, results_display
# Import AppService if needed directly by home_main, otherwise handled by session_state init
# from src.server.main import AppService

def main():
    # Removed st.set_page_config(layout="wide") from here
    st.title("Matching Automatique de Factures avec OCR")

    # Initialize session state here, specific to the home page logic
    initialize_session_state() # This now correctly handles AppService instantiation internally

    # Render components
    bank_statement, invoices = file_upload.render_file_upload()
    control_buttons.render_control_buttons(bank_statement, invoices)

    # Handle processing based on state
    if st.session_state.uploading:
        st.write("Uploading...")
        processing_logic.process_upload_and_extraction(bank_statement, invoices)

    #if st.session_state.matching:
    #    processing_logic.process_matching()

    # Display results
    # results_display.display_results()

# Removed if __name__ == "__main__": block as this file is meant to be imported as a module 