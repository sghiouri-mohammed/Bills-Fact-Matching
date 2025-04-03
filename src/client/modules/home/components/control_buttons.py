import streamlit as st
from src.client.modules.home.components.payment_form import render_payment_form
from src.client.modules.home.components.checkout_items import render_checkout_items
from src.client.modules.home.components.preview_data import render_preview_data

def handle_threshold_change():
    if st.session_state.invoices_list:
        st.session_state.is_slider_changed = True

def render_control_buttons(bank_statement, invoices,):
    files_selected = bank_statement and invoices and len(invoices) > 0    

    if files_selected:
         # Threshold slider, if the invoice are processed already we will call the display_results function with the list_view, on change
        st.session_state.treshold = st.slider("Seuil de correspondance", min_value=0, max_value=100, value=70, step=1, on_change = handle_threshold_change)
        render_preview_data(bank_statement, invoices)
        render_checkout_items(st.session_state.preview_data_frame, st.session_state.preview_invoices)
        render_payment_form(st.session_state.preview_bank_statement, st.session_state.preview_invoices)
         