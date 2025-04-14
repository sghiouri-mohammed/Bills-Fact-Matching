import streamlit as st

def main():
    st.header("About")
    st.markdown("""
        ### INOVERT : Matching Automatique de Factures à un Relevé Bancaire

        Cette application a été développée pour automatiser le processus de rapprochement entre les factures et les transactions bancaires, une tâche généralement chronophage et sujette aux erreurs lorsqu'elle est réalisée manuellement.

        ### Comment ça fonctionne ?

        Notre application utilise une technologie avancée de traitement d'images (Pixtral) et des algorithmes de matching intelligents pour :

        - **Extraire les données essentielles** de vos factures au format image (JPG/PNG) : montants, dates, commerçants
        - **Analyser votre relevé bancaire** au format CSV
        - **Établir automatiquement les correspondances** entre chaque transaction bancaire et la facture associée

        ### Avantages

        - **Gain de temps considérable** : quelques secondes suffisent pour traiter des dizaines de factures
        - **Réduction des erreurs** : notre algorithme identifie les correspondances avec précision
        - **Interface intuitive** : simple glisser ou déposer de vos fichiers
        - **Visualisation claire** des résultats et des correspondances trouvées

        ### Confidentialité

        Vos données financières restent confidentielles et ne sont pas stockées sur nos serveurs. Tout le traitement est effectué localement dans votre navigateur.

        ### Développé par

        Cette application a été développée dans le cadre d'un projet étudiant à HETIC par :

        - **SOBGUI Ivan Joel**
        - **OUMAR Ben Lol**
        - **SGHIOURI Mohammed**
        - **BOTI Armel Cyrille**
        - **DIVENGI KIBANGUDI BUNKEMBO Nagui**

        @Copyrigth 2025
        """)