import os
import pandas as pd
import logging
import time
import plotly.graph_objects as go

def create_confusion_matrix_plot(confusion_matrix):
    """Create a plotly heatmap for confusion matrix visualization"""
    labels = ['Négatif', 'Positif']
    
    fig = go.Figure(data=go.Heatmap(
        z=confusion_matrix,
        x=labels,
        y=labels,
        text=[[str(val) for val in row] for row in confusion_matrix],
        texttemplate="%{text}",
        textfont={"size": 16},
        colorscale='RdYlBu',
        showscale=True
    ))
    
    fig.update_layout(
        title='Matrice de Confusion',
        xaxis_title='Prédiction',
        yaxis_title='Réalité',
        width=400,
        height=400
    )
    
    return fig

def display_results(st, invoice_path=None, invoice={}, matching_results=[], confusion_results=None):
    """
    Display results including extracted data, matches, and performance metrics.
    
    Args:
        st: Streamlit instance
        invoice_path: Path to the invoice image
        invoice: Dictionary containing extracted invoice data
        matching_results: List of matching results
        confusion_results: Dictionary containing confusion matrix and metrics
    """
    extraction_info = invoice
    matching_result = matching_results
    
    #st.subheader(f"📄 Facture: {os.path.basename(invoice_path)}")
    col1, col2 = st.columns([1, 2])

    with col1:
        try:
            st.image(invoice_path, caption="Facture", use_container_width=True)
        except Exception as img_err:
            st.error(f"Could not load image {os.path.basename(invoice_path)}: {img_err}")

        # Display performance metrics if available
        if confusion_results:
            st.markdown("### 📊 Métriques de Performance")
            metrics = confusion_results['metrics']
            
            # Create three columns for metrics
            m1, m2, m3, m4 = st.columns(4)
            
            with m1:
                st.metric("Accuracy", f"{metrics['accuracy']:.1f}%")
            with m2:
                st.metric("Precision", f"{metrics['precision']:.1f}%")
            with m3:
                st.metric("Recall", f"{metrics['recall']:.1f}%")
            with m4:
                st.metric("F1-Score", f"{metrics['f1_score']:.1f}%")
            
            # Display confusion matrix
            st.markdown("### Matrice de Confusion")
            fig = create_confusion_matrix_plot(confusion_results['confusion_matrix'])
            st.plotly_chart(fig, use_container_width=True)

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

