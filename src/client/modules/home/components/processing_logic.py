import streamlit as st
import os
import time
import logging
from src.client.modules.home.components.results_display import display_results, create_confusion_matrix_plot
import pandas as pd
from src.server.config.paths import CSV_DIR, IMAGES_DIR
import numpy as np

def combine_confusion_matrices(matrices_list):
    """Combine multiple confusion matrices into one global matrix"""
    if not matrices_list:
        return None
    
    # Initialize the global matrix with zeros
    global_matrix = np.zeros((2, 2), dtype=int)
    
    # Sum all individual matrices
    for matrix in matrices_list:
        if matrix is not None:
            global_matrix += np.array(matrix["confusion_matrix"])
    
    # Calculate global metrics
    TP = global_matrix[1, 1]
    FP = global_matrix[0, 1]
    TN = global_matrix[0, 0]
    FN = global_matrix[1, 0]
    
    total = TP + FP + TN + FN
    accuracy = (TP + TN) / total if total > 0 else 0
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "confusion_matrix": global_matrix.tolist(),
        "metrics": {
            "accuracy": accuracy * 100,
            "precision": precision * 100,
            "recall": recall * 100,
            "f1_score": f1 * 100
        },
        "counts": {
            "true_positive": int(TP),
            "false_positive": int(FP),
            "true_negative": int(TN),
            "false_negative": int(FN)
        }
    }

def process_upload_and_extraction(bank_statement, invoices):
    """Process the upload and extraction of data from invoices"""
    status_placeholder = st.empty()
    progress_bar = st.progress(0)
    
    is_processing = True
    num_invoices = len(st.session_state.preview_invoices)
    
    # Initialize the list to store all confusion matrices
    if 'confusion_matrices' not in st.session_state:
        st.session_state.confusion_matrices = []
    else:
        st.session_state.confusion_matrices = []
    
    try:
        with st.container(height=600):
            st.markdown("<hr>", unsafe_allow_html=True)
            status_placeholder.info("🔄 Uploading files and extracting data...")
    
            # Display header for all results
            st.header("📊 Analyse des Factures")
            st.markdown("""
            Pour chaque facture, nous analysons la correspondance avec les données bancaires.
            Les résultats de performance globaux seront affichés à la fin du traitement.
            """)

            st.session_state.can_upload = False
            
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

                    st.session_state.invoices_list = [*st.session_state.invoices_list, [invoice_path, extracted_data]]

                    # Process matching for this invoice
                    matching_results, confusion_results = process_matching(invoice_path, invoice_name, extracted_json)
                    
                    # Store confusion matrix for global calculation
                    if confusion_results:
                        st.session_state.confusion_matrices.append(confusion_results)
                    
                    # Update progress
                    progress = 10 + int(90 * (i + 1) / num_invoices)
                    progress_bar.progress(progress)

                    st.button(f"Path: {invoice_path}")
                    
                    st.session_state.list_view = [*st.session_state.list_view, [invoice_path, extracted_data, matching_results]]
                    
                    # Display individual results without confusion matrix
                    if not st.session_state.is_slider_changed:
                        display_results(st, invoice_path, extracted_data, matching_results, None)

            else:
                st.session_state.invoices_list_slider = st.session_state.invoices_list
                for invoice in st.session_state.invoices_list_slider:
                    # Process matching for this invoice
                    matching_results, _ = process_matching(invoice[0], os.path.basename(invoice[0]), invoice[1].get('json'))
                    display_results(st, invoice[0], invoice[1], matching_results, None)
            
            # All invoices processed
            progress_bar.progress(100)
            status_placeholder.success("✅ Upload and data extraction complete!")
            time.sleep(1)
            status_placeholder.empty()

            is_processing = False
            
            st.markdown("<hr>", unsafe_allow_html=True)
        
        # Add the results section with global confusion matrix at the end
        if not is_processing:
            st.divider()
            st.header("Résultats Globaux:")
            
            # Calculate and display global confusion matrix
            global_conf_matrix = combine_confusion_matrices(st.session_state.confusion_matrices)
            
            if global_conf_matrix:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("### 📊 Matrice de Confusion Globale")
                    st.markdown("""
                    - **TP (True Positive)** : Factures correctement matchées
                    - **TN (True Negative)** : Absence de match correctement identifiée
                    - **FP (False Positive)** : Match incorrect proposé
                    - **FN (False Negative)** : Match manqué
                    """)
                    
                    fig = create_confusion_matrix_plot(global_conf_matrix["confusion_matrix"])
                    st.plotly_chart(fig, use_container_width=True, key="global_matrix")
                
                with col2:
                    st.markdown("### 📈 Métriques de Performance")
                    metrics = global_conf_matrix["metrics"]
                    counts = global_conf_matrix["counts"]
                    
                    # Display counts
                    st.markdown("#### Décompte:")
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        st.metric("True Positives", counts["true_positive"])
                    with c2:
                        st.metric("False Positives", counts["false_positive"])
                    with c3:
                        st.metric("True Negatives", counts["true_negative"])
                    with c4:
                        st.metric("False Negatives", counts["false_negative"])
                    
                    # Display performance metrics
                    st.markdown("#### Métriques:")
                    m1, m2, m3, m4 = st.columns(4)
                    with m1:
                        st.metric("Accuracy", f"{metrics['accuracy']:.1f}%")
                    with m2:
                        st.metric("Precision", f"{metrics['precision']:.1f}%")
                    with m3:
                        st.metric("Recall", f"{metrics['recall']:.1f}%")
                    with m4:
                        st.metric("F1-Score", f"{metrics['f1_score']:.1f}%")
            
            # Display individual results table
            st.header("Résultats Détaillés:")
            if not st.session_state.result_list.empty:
                st.dataframe(st.session_state.result_list, use_container_width=True)
                
                file_type = st.sidebar.selectbox("Select the download file type", ["CSV", "XLS"])
                converted_data = st.session_state.server_service.download_file(st.session_state.result_list)
                if file_type == 'CSV':
                    st.download_button(
                        label="Download CSV",
                        data=converted_data,
                        file_name="matching_results.csv",
                        mime="text/csv",
                    )
                else:
                    st.download_button(
                        label="Download Excel",
                        data=converted_data,
                        file_name="matching_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )  
            else:
                st.markdown(f"### Aucun résultat trouvé pour les {num_invoices} factures avec ce relevé bancaire.")
            
            st.button("🧹 Recommencer et éffectuez un nouveau payment ?", key="clear_button", on_click=handle_clear_service)
            

    except Exception as e:
        logging.error(f"Upload/Extraction Error: {e}", exc_info=True)
        st.error(f"An error occurred during upload/extraction: {e}")
        st.session_state.uploading = False
        st.session_state.extracted_data = {}
        st.session_state.matching_results = {}
        st.session_state.invoices_list = []
        st.session_state.bank_statement_path = None

def handle_clear_service():
    """Reset all session state variables and delete files."""
    try:
        if st.session_state.bank_statement_path and os.path.exists(st.session_state.bank_statement_path):
            st.session_state.server_service.delete_file(st.session_state.bank_statement_path)
        for invoice_path in st.session_state.invoices_list:
            if isinstance(invoice_path, list) and len(invoice_path) > 0:
                path = invoice_path[0]
                if os.path.exists(path):
                    st.session_state.server_service.delete_file(path)
            elif os.path.exists(invoice_path):
                st.session_state.server_service.delete_file(invoice_path)
    except Exception as e:
        logging.error(f"Error deleting files during clear: {e}")

    # Reset all session state variables
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
    st.session_state.confusion_matrices = []
    st.session_state.result_list = pd.DataFrame()
    st.session_state.can_upload = True
    st.session_state.is_slider_changed = False
    st.session_state.invoices_list_slider = []
    st.session_state.list_view = []
    st.session_state.preview_bank_statement = None
    st.session_state.preview_invoices = []
    st.session_state.treshold = 70
    
    logging.info("State cleared by user.")
    st.success("Result cleared. You can upload new files.")

def process_matching(invoice_path, invoice_name, invoice_data):
    """Process matching for a single invoice"""
    try:
        if not st.session_state.bank_statement_path:
            st.error("Bank statement path not found.")
            return [], None

        # En cas d'échec d'extraction (erreur API), invoice_data peut être vide
        # Dans ce cas, on considère comme un Faux Négatif (FN)
        is_extraction_failed = not invoice_data
        
        if is_extraction_failed:
            st.warning(f"📋 Extraction échouée pour {os.path.basename(invoice_path)}. Considéré comme un Faux Négatif.")
            
            # Créer une matrice de confusion manuelle pour FN
            confusion_results = {
                "confusion_matrix": [[0, 0], [1, 0]],  # [TN, FP], [FN, TP]
                "metrics": {
                    "accuracy": 0.0,
                    "precision": 0.0,
                    "recall": 0.0,
                    "f1_score": 0.0
                },
                "counts": {
                    "true_positive": 0,
                    "false_positive": 0,
                    "true_negative": 0,
                    "false_negative": 1
                }
            }
            
            return [], confusion_results

        # Si l'extraction a réussi, continuer avec le matching normal
        try:
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
                
                # Si une correspondance est trouvée, l'ajouter à result_list
                if match_list and len(match_list) > 0:
                    match_df = pd.DataFrame(match_list)
                    
                    if 'match_score' in match_df.columns:
                        # Trouver le score maximal
                        max_score = match_df['match_score'].max()
                        
                        # Obtenir la(les) ligne(s) avec le score maximal
                        row_with_max_score = match_df[match_df['match_score'] == max_score].copy()
                        # Ajouter une colonne source
                        row_with_max_score['source'] = invoice_name
                        
                        # Initialiser result_list si nécessaire
                        if not hasattr(st.session_state, 'result_list'):
                            st.session_state.result_list = pd.DataFrame()
                        
                        # Ajouter à result_list s'il n'est pas vide
                        if not st.session_state.result_list.empty:
                            st.session_state.result_list = pd.concat([st.session_state.result_list, row_with_max_score], ignore_index=True)
                        else:
                            st.session_state.result_list = row_with_max_score

            return match_list, confusion_results
        
        except Exception as e:
            logging.error(f"Matching Error for {invoice_path}: {e}", exc_info=True)
            st.error(f"An error occurred during matching for {invoice_path}: {e}")
            
            # En cas d'erreur de matching, considérer comme un Faux Négatif également
            confusion_results = {
                "confusion_matrix": [[0, 0], [1, 0]],  # [TN, FP], [FN, TP]
                "metrics": {
                    "accuracy": 0.0,
                    "precision": 0.0,
                    "recall": 0.0,
                    "f1_score": 0.0
                },
                "counts": {
                    "true_positive": 0,
                    "false_positive": 0,
                    "true_negative": 0,
                    "false_negative": 1
                }
            }
            
            return [], confusion_results

    except Exception as e:
        logging.error(f"Processing Error for {invoice_path}: {e}", exc_info=True)
        st.error(f"An error occurred during processing for {invoice_path}: {e}")
        return [], None