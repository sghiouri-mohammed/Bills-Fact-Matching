import streamlit as st
import pandas as pd
from io import BytesIO

def render_preview_data(bank_statement, invoices):
    st.subheader("📊 Prévisualisation des données")

    # Bank Statement Section
    with st.expander("📄 Aperçu du relevé bancaire", expanded=True):
        st.markdown("<hr>", unsafe_allow_html=True)
        if bank_statement:
            st.markdown("### Informations du relevé bancaire")
            st.markdown(f"📁 Nom du fichier: {bank_statement.name}")
            
            # Create a copy of the bank statement file
            copy_bank_statement = {
                "name": bank_statement.name,
                "read": bank_statement.read()
            }
            
            file = BytesIO(copy_bank_statement['read'])
            st.session_state.preview_bank_statement = copy_bank_statement
            st.session_state.preview_data_frame = pd.read_csv(file, sep=',', encoding='utf-8')
            
            if not st.session_state.preview_data_frame.empty:
                st.markdown("### Données du relevé bancaire")
                st.dataframe(
                    st.session_state.preview_data_frame.style.set_properties(**{
                        'background-color': 'white',
                        'color': 'black',
                        'border-color': 'white',
                    }),
                    height=400,
                    #width=-1
                )
        st.markdown("<hr>", unsafe_allow_html=True)

    # Invoices Section
    with st.expander("📂 Aperçu des factures", expanded=True):
        st.markdown("<hr>", unsafe_allow_html=True)
        if invoices:
            st.markdown("### Liste des factures téléchargées")
            st.markdown(f"📁 Nombre de factures: {len(invoices)}")
            
            # Create copies of all invoice files
            copy_invoices = []
            for invoice in invoices:
                copy_invoices.append({
                    "name": invoice.name,
                    "read": invoice.read()
                })
            st.session_state.preview_invoices = copy_invoices

            # Display images in a grid layout
            if st.session_state.preview_invoices:
                st.markdown("### Prévisualisation des factures")
                
                # Create a container with multiple columns and horizontal scroll
                st.markdown("""
                <div style="overflow-x: auto; display: flex; flex-wrap: nowrap; background-color: #f5f5f5; padding: 20px; border-radius: 8px;">
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; padding: 10px;">
                """, unsafe_allow_html=True)
                
                # Create 3 columns
                cols = st.columns(3)
                
                # Display images in the columns
                for i, invoice in enumerate(st.session_state.preview_invoices):
                    with cols[i % 3]:
                        st.markdown(f"📄 {invoice['name']}", unsafe_allow_html=True)
                        image_file = BytesIO(invoice['read'])
                        st.image(
                            image_file,
                            width=200,
                            caption=f"Facture {i+1}",
                            output_format="auto"
                        )
                
                st.markdown("""
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

