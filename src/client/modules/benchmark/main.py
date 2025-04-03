import streamlit as st
from io import BytesIO
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns


def main():
    st.header("Benchmark")
    client_file = {
        'df': pd.DataFrame()
    }
    ai_file = {
        'df': pd.DataFrame()
    }
    
    st.subheader("1. Relevé Bancaire avec correspondance fourni par notre application :")
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

            st.markdown("## 📊 Résultats du Benchmark")
            
            # Affichage des principales métriques avec interprétations dynamiques
            col1, col2, col3, col4 = st.columns(4)

            def interpret(score):
                if score >= 90:
                    return "✅ Très bon"
                elif score >= 70:
                    return "👍 Correct"
                elif score >= 50:
                    return "⚠️ À améliorer"
                else:
                    return "❌ Insuffisant"

            # Accuracy
            acc = display_data['accuracy']
            col1.metric("🎯 Accuracy", f"{acc:.2f} %", interpret(acc))

            # Precision
            prec = display_data['precision']
            col2.metric("🔍 Precision", f"{prec:.2f} %", interpret(prec))

            # Recall
            rec = display_data['recall']
            col3.metric("📢 Recall", f"{rec:.2f} %", interpret(rec))

            # F1 Score
            f1 = display_data['f1_score']
            col4.metric("⚖️ F1 Score", f"{f1:.2f} %", interpret(f1))


            with st.expander("🧠 Comment interpréter ces métriques ?"):
                st.markdown("""
                - **🎯 Accuracy** : Proportion de prédictions correctes. Plus ce chiffre est proche de 100%, plus le modèle est fiable dans l’ensemble.
                - **🔍 Precision** : Indique parmi les transactions détectées comme "correspondantes", combien le sont réellement. Utile pour éviter les faux positifs.
                - **📢 Recall** : Indique parmi toutes les vraies correspondances, combien ont été bien identifiées. Important pour ne rien rater.
                - **⚖️ F1 Score** : Moyenne entre la précision et le rappel. Il donne une vision équilibrée de la performance du modèle.
                """)

            with st.container():
                st.markdown("## 📄 Rapport de Classification")

                report_text = display_data["classification_report"]

                try:
                    # Extraction ligne par ligne
                    lines = report_text.strip().split('\n')
                    lines = [line for line in lines if line.strip() != '']

                    headers = ["class"] + lines[0].split()
                    data = []

                    for line in lines[1:]:
                        parts = line.split()
                        if len(parts) >= 5:
                            label = parts[0]
                            values = parts[1:5]
                            data.append([label] + values)

                    df_report = pd.DataFrame(data, columns=headers)
                    st.dataframe(df_report, use_container_width=True)
                except Exception as e:
                    st.warning(f"Impossible de convertir le rapport en tableau : {e}")
                    st.text(report_text)

            

            # Matrice de confusion
            confusion_df = pd.DataFrame(display_data["confusion_matrix"])

            # Matrice brute (tableau)
            # st.dataframe(confusion_df, use_container_width=True)

            # Heatmap
            st.markdown("## 📊 Matrice de Confusion (Heatmap)")

            fig, ax = plt.subplots(figsize=(6, 4))
            sns.heatmap(confusion_df, annot=True, fmt='d', cmap='Blues', cbar=True, ax=ax)
            ax.set_xlabel("Classe prédite")
            ax.set_ylabel("Classe réelle")
            ax.set_title("Matrice de Confusion - Visualisation")
            st.pyplot(fig)