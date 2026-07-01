"""Cliente para Evolution API."""
import requests
from typing import Optional, Dict, Any
from loguru import logger

from config.settings import (
    EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE_NAME
)


class EvolutionAPI:
    """Cliente para interactuar con Evolution API."""
    
    def __init__(self):
        """Inicializa el cliente de Evolution API."""
        self.base_url = EVOLUTION_API_URL.rstrip('/')
        self.api_key = EVOLUTION_API_KEY
        self.instance_name = EVOLUTION_INSTANCE_NAME
        self.headers = {
            'apikey': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def send_message(self, telefono: str, mensaje: str) -> bool:
        """Envía un mensaje de texto por WhatsApp."""
        url = f"{self.base_url}/message/sendText/{self.instance_name}"
        
        # El número ya viene con código de país desde WhatsApp remoteJid
        # (ej: 573023373311 para Colombia, 15169744621 para US)
        
        payload = {
            "number": telefono,
            "text": mensaje
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            logger.info("Mensaje de WhatsApp enviado")
            return True
        except requests.exceptions.RequestException as e:
            logger.error("Error enviando mensaje de WhatsApp: {}", type(e).__name__)
            return False
    
    def get_instance_status(self) -> Optional[Dict[str, Any]]:
        """Obtiene el estado de la instancia."""
        url = f"{self.base_url}/instance/connectionState/{self.instance_name}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo estado de instancia: {e}")
            return None
    
    def get_qr_code(self) -> Optional[Dict[str, Any]]:
        """Obtiene el código QR para conectar WhatsApp."""
        url = f"{self.base_url}/instance/connect/{self.instance_name}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo QR: {e}")
            return None
