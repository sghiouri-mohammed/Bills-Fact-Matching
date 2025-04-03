import streamlit as st
from io import BytesIO
import pandas as pd

def main():
    st.header("Benchmark")
    client_file = {
        'df': pd.DataFrame()
    }
    ai_file = {
        'df': pd.DataFrame()
    }
    
    st.subheader("1. Relevé Bancaire avec correspondance fourni par notre application:")
    if st.session_state.result_list.empty:
        predicted_file = st.file_uploader("SVP, donnez le résultat de la correspondance", type=['csv'], key="ai_bank_uploader_widget")
        if predicted_file:
            ai_file = {
                'name': predicted_file.name,
                'df':  pd.read_csv(BytesIO(predicted_file.read()), sep=',', encoding='utf-8')
            }
        
    else:
        st.dataframe(st.session_state.result_list, use_container_width=True)
    
    st.subheader("2. Relevé Bancaire et label pour faire le test de comparaison")
    target_file = st.file_uploader("Relevé bancaire (CSV) et Label", type=['csv'], key="target_bank_uploader_widget")
    if target_file:
        client_file = {
            'name': target_file.name,
            'df':  pd.read_csv(BytesIO(target_file.read()), sep=',', encoding='utf-8')
        }

    if not client_file.get('df').empty and not ai_file.get('df').empty:
        benchmark = st.session_state.server_service.benchmark(client_file.get('df'), ai_file.get('df'))
        if benchmark:
            display_data = {k: (v if v is not None else "N/A") for k, v in benchmark.items()}
            st.json(display_data)