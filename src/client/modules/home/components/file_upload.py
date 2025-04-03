import streamlit as st

def render_file_upload():
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Relevé Bancaire")
        bank_statement = st.file_uploader("Relevé bancaire (CSV)", type=['csv'], key="bank_uploader_widget")
    with col2:
        st.subheader("2. Factures")
        invoices = st.file_uploader("Factures (JPG, JPEG, PNG)", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True, key="invoices_uploader_widget")
    return bank_statement, invoices 