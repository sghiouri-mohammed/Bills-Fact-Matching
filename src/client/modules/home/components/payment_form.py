import streamlit as st

def render_payment_form(bank_statement, invoices):
    st.subheader("Paiement")
    files_selected = bank_statement and invoices and len(invoices) > 0
    can_upload = files_selected and not st.session_state.uploading and not st.session_state.matching and not st.session_state.results_ready
    st.session_state.is_paid = False
    
    with st.form("payment_form"):
        col1, col2 = st.columns(2)

        with col1:
            card_number = st.text_input("Card Number", type="password", placeholder="•••• •••• •••• ••••", value="1234 5678 9012 3456")
            expiration_date = st.text_input("Expiration Date", placeholder="MM/YY", value="01/25")
        
        with col2:
            cvc = st.number_input("CVC", min_value=100, max_value=999, value=123)

        # display the total amount to pay in a box with a border, with green background and center text, put a bold text
        st.markdown(f"<div style='border: 1px solid #ccc; padding: 10px; background-color: #00ff00; border-radius: 5px; text-align: center; font-weight: bold; font-size: 20px;'>Montant total à payer: {st.session_state.total_amount} EUR</div>", unsafe_allow_html=True)
        
        save_payment = st.checkbox("Save payment information")
        
        if not st.session_state.is_paid:
            if st.form_submit_button("Pay"):
                st.session_state.is_paid = True
                st.success("Payment processed successfully!")

    def on_click_upload():
        st.session_state.uploading = True
        st.session_state.is_service_cleared = False
        # st.rerun()

    if st.session_state.is_paid and can_upload:
        st.button("🚀 Begin Extraction", key="upload_button", on_click=on_click_upload)
            
