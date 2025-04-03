import json
import logging
import base64
import os
import requests
import time
from typing import Dict, Any, List
from ..config.settings import (
    MISTRAL_API_KEY,
    MISTRAL_API_BASE_URL,
    MISTRAL_MODEL,
    MAX_RETRIES,
    REQUEST_TIMEOUT,
    MAX_TOKENS,
    TEMPERATURE
)

logger = logging.getLogger('ExtractData')

class MistralClient:
    def __init__(self, api_key: str = MISTRAL_API_KEY):
        self.api_key = api_key
        self.base_url = MISTRAL_API_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _make_request_with_retry(self, messages: List[Dict[str, Any]], max_retries: int = MAX_RETRIES) -> Any:
        """
        Fait une requête à l'API avec retry en cas d'erreur
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Tentative {attempt + 1}/{max_retries} d'appel à l'API Mistral")
                logger.info(f"Messages envoyés: {json.dumps(messages, indent=2, ensure_ascii=False)}")
                
                payload = {
                    "model": MISTRAL_MODEL,
                    "messages": messages,
                    "temperature": TEMPERATURE,
                    "max_tokens": MAX_TOKENS
                }
                
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=REQUEST_TIMEOUT
                )
                
                if response.status_code != 200:
                    logger.error(f"Erreur API: {response.status_code} - {response.text}")
                    raise Exception(f"Status: {response.status_code}. Message: {response.text}")
                
                result = response.json()
                logger.info("Réponse reçue de l'API Mistral")
                logger.info(f"Réponse: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                if not result.get('choices') or not result['choices'][0].get('message', {}).get('content'):
                    raise Exception("Réponse invalide de l'API")
                    
                return result
                
            except Exception as e:
                logger.error(f"Erreur lors de l'appel à l'API (tentative {attempt + 1}): {str(e)}")
                if attempt == max_retries - 1:
                    logger.error("Nombre maximum de tentatives atteint")
                    raise e
                wait_time = 2 ** attempt
                logger.info(f"Attente de {wait_time} secondes avant la prochaine tentative")
                time.sleep(wait_time)

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


