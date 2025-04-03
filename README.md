# Projet d'Extraction de Données de Reçus par OCR

## Objectif du Projet

Ce projet vise à extraire automatiquement des informations clés à partir d'images de reçus ou de factures en utilisant la reconnaissance optique de caractères (OCR). Les informations extraites incluent typiquement la date, le montant total, la devise et le nom du vendeur. L'objectif est de simplifier la saisie de données ou la gestion des dépenses. Le script `src/server/extract_data.py` utilise le model Pixtral de Mistral qui contient le ``Computer Vision`` pour effectuer l'OCR et ensuite analyser le texte brut pour en extraire ces informations structurées.

## Structure du Projet

Le projet est organisé comme suit :

├── src/ # Dossier contenant le code source principal <br>
│ ├── client/ # Modules liés au client avec Streamlit  <br>
│ ├── server/ # Modules liés au backend / logique métier <br>
│ │ ├── init.py <br>
│ │ ├── extract_data.py # Logique d'extraction OCR via Nanonets <br>
│ │ ├── config.py # Fichier pour stocker la clé API Nanonets <br>
│ │ └── ... # Autres modules serveur possibles <br>
│ └── main.py # L'entrée principale du  fichier source <br>
├── storage # Le dossier temporaire pour upload les fichiers <br>
├── init.py # Script principal / Point d'entrée de l'application Streamlit <br>
├── requirements.txt # Liste des dépendances Python du projet <br>
├── .venv/ # Environnement virtuel Python (créé localement) <br>
└── README.md # Ce fichier d'information

## Dépendances

Lisez le requirements.txt: <a href='requirements.txt'>Pré-requis</a>


## Installation et Lancement.

Suivez ces étapes pour configurer et lancer le projet :

1.  **Cloner le dépôt** (si applicable) :
    ```bash
    git clone <url-du-depot>
    cd <nom-du-dossier-du-projet>
    ```

2.  **Créer un environnement virtuel** :
    Il est fortement recommandé d'utiliser un environnement virtuel pour isoler les dépendances du projet.
    ```bash
    python -m venv venv
    ```
    Activez l'environnement :
    *   Sur Windows :
        ```bash
        .\venv\Scripts\activate
        ```
    *   Sur macOS/Linux :
        ```bash
        source venv/bin/activate
        ```

3.  **Installer les dépendances** :
    Assurez-vous que toutes les bibliothèques nécessaires sont listées dans `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```
    *(Note : Assurez-vous que `requirements.txt` contient au moins `nanonets-ocr` et `streamlit` si vous utilisez Streamlit).*

4.  **Configurer vos clés API et paramètres** :
    *   Ouvrez le fichier `.env`.
    *   Remplacez la valeur de `MISTRAL_API_KEY` par votre propre clés.
    ```python:.env
    # Configuration de l'API Mistral
    MISTRAL_API_KEY=

    # Configuration de l'application
    DEBUG=True
    LOG_LEVEL=DEBUG

    # Configuration des timeouts
    REQUEST_TIMEOUT=30
    MAX_RETRIES=3

    # Configuration du modèle
    MISTRAL_MODEL=pixtral-12b-2409
    MAX_TOKENS=131072
    TEMPERATURE=0.0
    ```

5.  **Lancer l'application** :
    Si vous utilisez Streamlit et que `init.py` est votre point d'entrée :
    ```bash
    streamlit run main.py
    ```

    L'application devrait maintenant être accessible dans votre navigateur web à l'adresse indiquée par Streamlit (généralement `http://localhost:8501`).
