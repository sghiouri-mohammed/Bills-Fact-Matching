import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de l'API Mistral
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
MISTRAL_API_BASE_URL = "https://api.mistral.ai/v1"
MISTRAL_MODEL = os.getenv('MISTRAL_MODEL', 'pixtral-12b-2409')

# Configuration de l'application
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')

# Configuration des timeouts
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))

# Configuration du modèle
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '131072'))
TEMPERATURE = float(os.getenv('TEMPERATURE', '0.0'))

# Validation des variables requises
if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY n'est pas définie dans le fichier .env")

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 