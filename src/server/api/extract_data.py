import json
import logging
import base64
import os
import requests
import time
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
import pandas as pd

from src.server.config.settings import (
    MISTRAL_API_KEY,
    MISTRAL_API_BASE_URL,
    MISTRAL_MODEL,
    MAX_RETRIES,
    REQUEST_TIMEOUT,
    MAX_TOKENS,
    TEMPERATURE
)

logger = logging.getLogger('ExtractData')
"""
load_dotenv()

# Récupérer les valeurs des variables d'environnement
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
print("================================ la cle aPI : ", MISTRAL_API_KEY)
MISTRAL_API_BASE_URL = os.getenv("MISTRAL_API_BASE_URL")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))  # Valeur par défaut 3 si non définie
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", 10.0))  # Valeur par défaut 10.0s
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1000))  # Valeur par défaut 1000
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))  # Valeur par défaut 0.7
logger = logging.getLogger('ExtractData')
"""
class MistralClient:
    def __init__(self, api_key: str = MISTRAL_API_KEY):
        self.api_key = api_key
        self.base_url = MISTRAL_API_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _make_request_with_retry(self, messages: List[Dict[str, Any]], max_attempts=3):
        """Make API request with retry logic."""
        attempt = 0
        
        while attempt < max_attempts:
            try:
                attempt += 1
                logging.info(f"Tentative {attempt}/{max_attempts} d'appel à l'API Mistral")
                
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": MISTRAL_MODEL,
                        "messages": messages,
                        "temperature": TEMPERATURE,
                        "max_tokens": MAX_TOKENS
                    },
                    timeout=REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    logging.info("Réponse reçue de l'API Mistral")
                    logging.info(f"Réponse: {response.text}")
                    return response.json()
                else:
                    logging.error(f"Erreur API: {response.status_code} - {response.text}")
                    
                    # Traiter spécifiquement les erreurs de rate limit
                    if response.status_code == 429:
                        wait_time = 5 * (2 ** attempt)  # Attente exponentielle: 5, 10, 20 secondes
                        logging.error(f"Erreur lors de l'appel à l'API (tentative {attempt}): Status: {response.status_code}. Message: {response.text}")
                        
                        if attempt < max_attempts:
                            logging.info(f"Attente de {wait_time} secondes avant la prochaine tentative")
                            time.sleep(wait_time)
                        else:
                            logging.error("Nombre maximum de tentatives atteint")
                            raise Exception(f"Status: {response.status_code}. Message: {response.text}")
                    else:
                        logging.error(f"Erreur lors de l'appel à l'API: Status: {response.status_code}. Message: {response.text}")
                        raise Exception(f"Status: {response.status_code}. Message: {response.text}")
            
            except requests.exceptions.RequestException as e:
                logging.error(f"Erreur de connexion à l'API (tentative {attempt}): {e}")
                
                if attempt < max_attempts:
                    wait_time = 2 ** attempt
                    logging.info(f"Attente de {wait_time} secondes avant la prochaine tentative")
                    time.sleep(wait_time)
                else:
                    logging.error("Nombre maximum de tentatives atteint")
                    raise e
        
        raise Exception("Nombre maximum de tentatives atteint sans succès")

    def send_message(self, messages: List[Dict[str, Any]]) -> str:
        """
        Envoie un message à l'API et retourne la réponse
        """
        response = self._make_request_with_retry(messages)
        return response['choices'][0]['message']['content']

def load_prompt() -> str:
    """Load the invoice extraction prompt from file."""
    prompt_path = os.path.join('./src/server/prompts', 'invoice_extraction.txt')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

def get_extracted_data(image_path: str) -> Dict[str, Any]:
    """Extract data from an image using Mistral Vision API."""
    try:
        # Initialize Mistral client
        mistral_client = MistralClient(api_key=MISTRAL_API_KEY)
        
        # Read and encode the image
        with open(image_path, 'rb') as image_file:
            image_content = image_file.read()
            image_base64 = base64.b64encode(image_content).decode('utf-8')

        # First, get the raw text from the image
        text_prompt = """Extract all text from this invoice image. Return only the raw text, without any formatting or analysis."""

        text_messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]

        logger.info(f"Extracting text from: {image_path}")
        raw_text = mistral_client.send_message(text_messages)
        
        if not raw_text:
            logger.warning(f"Mistral returned empty text for {image_path}")
            return {"success": False, "error": "OCR returned no text", "data": None}

        logger.debug(f"\n🔹 Raw extracted text:\n{raw_text}")

        # Now, analyze the text using the invoice extraction prompt
        analysis_prompt = load_prompt().format(invoice_text=raw_text)
        
        analysis_messages = [
            {
                "role": "user",
                "content": analysis_prompt
            }
        ]

        logger.info("Analyzing extracted text...")
        analysis_result = mistral_client.send_message(analysis_messages)
        
        try:
            # Clean up the response to ensure it's valid JSON
            analysis_result = analysis_result.strip()
            if analysis_result.startswith('```json'):
                analysis_result = analysis_result[7:]
            if analysis_result.endswith('```'):
                analysis_result = analysis_result[:-3]
            analysis_result = analysis_result.strip()
            
            extracted_data = json.loads(analysis_result)
            logger.info("\n🔹 Extracted Information:")
            logger.info(json.dumps(extracted_data, indent=2))

            return {
                "success": True,
                "data": {
                    "json": extracted_data,
                    "raw_text": raw_text
                }
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {"success": False, "error": "Failed to parse extracted data", "data": None}
        
    except Exception as e:
        logger.error(f"Error during OCR extraction for {image_path}: {e}", exc_info=True)
        return {"success": False, "error": str(e), "data": None}

# Définir le chemin de base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def read_csv(file_path):
    logging.debug(f"Reading CSV file: {file_path}")
    try:
        # Construire le chemin complet
        full_path = os.path.join(BASE_DIR, 'storage', 'dataset', 'csv', file_path)
        
        logging.debug(f"Full path to CSV file: {full_path}")
        if not os.path.exists(full_path):
            logging.error(f"CSV file not found at {full_path}")
            return None
        
        # Charger le CSV
        df = pd.read_csv(full_path)
        return df
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        return None


