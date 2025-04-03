import streamlit as st

def render_checkout_items(bank_statement, invoices):
    if not st.session_state.preview_data_frame.empty:
        st.subheader("Estimation des frais pour le prélèvement bancaire et les factures:")

        
        df = st.session_state.preview_data_frame
        
        col1, col2 = st.columns(2)

        with col1:
            # we will display the subt total of cost of the df for each row which cost 0.5 EUR, rounded to 2 decimal places
            sub_total_bank_statement = round(len(df) * 0.01, 2)
            st.write(f"Sous total Bancaire: number of rows: {len(df)} x 0.01 EUR = {sub_total_bank_statement} EUR")

        with col2:
            # we will display the sub total of cost for each invoice which cost 1 EUR, rounded to 2 decimal places
            sub_total_invoices = round(len(invoices) * 0.4, 2)
            st.write(f"Sous total Factures: number of invoices: {len(invoices)} x 0.40 EUR = {sub_total_invoices} EUR")
        
        st.session_state.total_amount = round(sub_total_bank_statement + sub_total_invoices, 2)
        st.write(f"Total: {st.session_state.total_amount} EUR")


