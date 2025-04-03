import streamlit as st
from src.server import APIService
import pandas as pd

def initialize_session_state():
    """
    Initialise les variables de session
    """
    if 'server_service' not in st.session_state:
        st.session_state.server_service = APIService()
    if 'invoices_list' not in st.session_state:
        st.session_state.invoices_list = []
    if 'extracted_data' not in st.session_state:
        st.session_state.extracted_data = {}
    if 'matching_results' not in st.session_state:
        st.session_state.matching_results = {}
    if 'uploading' not in st.session_state:
        st.session_state.uploading = False
    if 'matching' not in st.session_state:
        st.session_state.matching = False
    if 'bank_statement_path' not in st.session_state:
        st.session_state.bank_statement_path = None
    if 'results_ready' not in st.session_state:
        st.session_state.results_ready = False 
    if 'list_view' not in st.session_state:
        st.session_state.list_view = []
    if 'treshold' not in st.session_state:
        st.session_state.treshold = 70
    if 'invoices_list_slider' not in st.session_state:
        st.session_state.invoices_list_slider = []
    if 'is_slider_changed' not in st.session_state:
        st.session_state.is_slider_changed = False
    if 'total_amount' not in st.session_state:
        st.session_state.total_amount = 0
    if 'preview_bank_statement' not in st.session_state:
        st.session_state.preview_bank_statement = {}
    if 'preview_invoices' not in st.session_state:
        st.session_state.preview_invoices = []
    if 'preview_data_frame' not in st.session_state:
        st.session_state.preview_data_frame = pd.DataFrame()
    if 'is_service_cleared' not in st.session_state:
        st.session_state.is_service_cleared = False
    if 'result_list' not in st.session_state:
        st.session_state.result_list = pd.DataFrame()


