import streamlit as st
import os
import time
import logging
from src.client.modules.home.components.results_display import display_results
import pandas as pd
from src.server.config.paths import CSV_DIR, IMAGES_DIR
        

def process_upload_and_extraction(bank_statement, invoices):
    status_placeholder = st.empty()
    progress_bar = st.progress(0)
    
    is_processing = True
    num_invoices = len(st.session_state.preview_invoices)
    
    
    try:
            
        with st.container(height=600):
            st.markdown("<hr>", unsafe_allow_html=True)
            status_placeholder.info("🔄 Uploading files and extracting data...")
    
            # Display header for all results
            st.header("📊 Analyse des Factures")
            st.markdown("""
            Pour chaque facture, nous analysons :
            - **TP (True Positive)** : Facture correctement matchée
            - **TN (True Negative)** : Absence de match correctement identifiée
            - **FP (False Positive)** : Match incorrect proposé
            - **FN (False Negative)** : Match manqué
            """)

            st.session_state.can_upload = False
            #st.session_state.is_slider_changed = False
            
            
            
            if (not st.session_state.is_slider_changed or not st.session_state.invoices_list) or not st.session_state.is_service_cleared:
                # Upload bank statement
                bank_file = st.session_state.preview_bank_statement
                bank_statement_path = os.path.join(CSV_DIR, bank_file.get('name'))
                st.session_state.server_service.upload_file(bank_statement_path, bank_file.get('read'))
                st.session_state.bank_statement_path = bank_statement_path
                st.session_state.list_view = []
                progress_bar.progress(10)
                # Process each invoice sequentially
                
                for i, invoice_file in enumerate(st.session_state.preview_invoices):
                    # Add a separator between invoices
                    if i > 0:
                        st.markdown("---")
                    
                    # Display invoice number
                    st.subheader(f"Facture {i+1}/{num_invoices}")
                    
                    # Upload invoice
                    invoice_name = invoice_file.get('name')
                    invoice_path = os.path.join(IMAGES_DIR, invoice_name)
                    st.session_state.server_service.upload_file(invoice_path, invoice_file.get('read'))
                    
                    # Extract data
                    status_placeholder.info(f"🔄 Processing invoice {i+1}/{num_invoices}...")
                    result = st.session_state.server_service.get_extracted_data(invoice_path)
                    extracted_data = {}
                    if result and result['success']:
                        extracted_data = result['data']
                        raw_text = extracted_data.get('raw_text', '')
                        extracted_json = extracted_data.get('json', {})
                    else:
                        logging.error(f"Extraction failed for {invoice_path}: {result.get('error', 'Unknown error')}")
                        extracted_json = {}
                        raw_text = 'Extraction Failed'

                    # Store extracted data
                    st.session_state.extracted_data[invoice_path] = {
                        'json': extracted_json,
                        'raw_text': raw_text,
                        'error': result.get('error', None)
                    }

                    st.session_state.invoices_list= [*st.session_state.invoices_list, [invoice_path, extracted_data]]

                    # Process matching for this invoice
                    matching_results = process_matching(invoice_path, invoice_name, extracted_json)
                    
                    # Update progress
                    progress = 10 + int(90 * (i + 1) / num_invoices)
                    progress_bar.progress(progress)

                    st.button(f"Path: {invoice_path}")
                    
                    st.session_state.list_view = [*st.session_state.list_view, [invoice_path, extracted_data, matching_results]]
                    
                    if not st.session_state.is_slider_changed:
                        display_results(st, invoice_path, extracted_data, matching_results)

            else:
                st.session_state.invoices_list_slider = st.session_state.invoices_list
                for invoice in st.session_state.invoices_list_slider:
                    # Process matching for this invoice
                    matching_results = process_matching(invoice[0], invoice[1].get('json'))
                    display_results(st, invoice[0], invoice[1], matching_results)
            
            # All invoices processed
            progress_bar.progress(100)
            status_placeholder.success("✅ Upload and data extraction complete!")
            time.sleep(1)
            status_placeholder.empty()

            is_processing = False
            
            st.markdown("<hr>", unsafe_allow_html=True)
        
        # Add the clear button only once after all results
        if not is_processing:
            st.divider()
            st.header("Resultat Finale:")
            if not st.session_state.result_list.empty:
                st.header("Resultat Finale:")
                st.dataframe(st.session_state.result_list, use_container_width=True)
                
                file_type = st.sidebar.selectbox("Select the download file type", ["CSV", "XLS"])
                converted_data =  st.session_state.server_service.download_file(st.session_state.result_list)
                if file_type == 'CSV':
                    st.download_button(
                        label="Download CSV",
                        data=converted_data,
                        file_name="my_dataframe.csv",
                        mime="text/csv",
                    )
                else:
                  st.download_button(
                        label="Download Excel",
                        data=converted_data,
                        file_name="my_dataframe.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )  
                
            else:
                st.markdown(f"### Aucun resultat trouvé pour les {num_invoices} factures avec ce relévé bancaire.")
            
            st.button("🧹 Recommencer et éffectuez un nouveau payment ?", key="clear_button", on_click=handle_clear_service)
            

    except Exception as e:
        logging.error(f"Upload/Extraction Error: {e}", exc_info=True)
        st.error(f"An error occurred during upload/extraction: {e}")
        st.session_state.uploading = False
        st.session_state.extracted_data = {}
        st.session_state.matching_results = {}
        st.session_state.invoices_list = []
        st.session_state.bank_statement_path = None
        # st.rerun()    
            
def handle_clear_service():
    try:
        if st.session_state.bank_statement_path and os.path.exists(st.session_state.bank_statement_path):
            st.session_state.server_service.delete_file(st.session_state.bank_statement_path)
        for invoice_path in st.session_state.invoices_list:
            if os.path.exists(invoice_path):
                st.session_state.server_service.delete_file(invoice_path)
    except Exception as e:
        logging.error(f"Error deleting files during clear: {e}")

    st.session_state.is_paid = False
    st.session_state.uploading = False
    st.session_state.matching = False
    st.session_state.is_service_cleared = True
    st.session_state.extracted_data = {}
    st.session_state.matching_results = {}
    st.session_state.invoices_list = []
    st.session_state.bank_statement_path = None
    st.session_state.results_ready = False
    st.session_state.total_amount = 0
    
    logging.info("State cleared by user.")
    st.success("Result cleared. You can upload new files.")
    # time.sleep(1)

def process_matching(invoice_path, invoice_name, invoice_data):
    """Process matching for a single invoice"""
    try:
        if not st.session_state.bank_statement_path:
            st.error("Bank statement path not found.")
            return []

        if not invoice_data:
            st.error("Extracted invoice data not found.")
            return []

        # Get matching results for this invoice
        match_list = st.session_state.server_service.get_matching_rows(
            st.session_state.bank_statement_path,
            invoice_data,
            threshold=st.session_state.treshold
        )

        # Calculate confusion matrix
        confusion_results = None
        if match_list is not None:
            confusion_results = st.session_state.server_service.calculate_confusion_matrix(
                st.session_state.bank_statement_path,
                match_list,
                invoice_name
            )

        if not st.session_state.is_slider_changed:
            display_results(st, invoice_path, invoice_data, match_list, confusion_results)

        return match_list

    except Exception as e:
        logging.error(f"Matching Error for {invoice_path}: {e}", exc_info=True)
        st.error(f"An error occurred during matching for {invoice_path}: {e}")
        return [] 