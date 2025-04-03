import os
import pandas as pd
import logging
import time

def display_results(st,invoice_path=None, invoice ={}, matching_results=[]):
    extraction_info = invoice
    matching_result = matching_results
    
    #st.subheader(f"📄 Facture: {os.path.basename(invoice_path)}")
    col1, col2 = st.columns([1, 2])

    with col1:
        try:
            st.image(invoice_path, caption="Facture", use_container_width=True)
        except Exception as img_err:
            st.error(f"Could not load image {os.path.basename(invoice_path)}: {img_err}")

    with col2:
        extracted_data = extraction_info.get('json', {})
        raw_text = extraction_info.get('raw_text', 'N/A')

        st.markdown("**📝 Données extraites :**")
        if extracted_data:
            display_data = {k: (v if v is not None else "N/A") for k, v in extracted_data.items()}
            st.json(display_data)
        else:
            st.warning("No structured data could be extracted.")

        st.markdown("**🏦 Correspondances trouvées :**")
        if matching_result:
            match_df = pd.DataFrame(matching_result)
            display_columns = ['match_score', 'date', 'amount', 'currency', 'vendor']
            for col in display_columns:
                if col not in match_df.columns:
                    match_df[col] = 'N/A'
            match_df = match_df[display_columns]
            match_df['match_score'] = match_df['match_score'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
            st.dataframe(match_df, use_container_width=True)
        else:
            st.info("Aucune correspondance trouvée dans le relevé bancaire pour cette facture (seuil de score non atteint).")

        with st.expander("Voir le texte brut extrait"):
            st.text(raw_text)    

