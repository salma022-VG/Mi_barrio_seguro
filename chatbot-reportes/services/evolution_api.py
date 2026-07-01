"""Cliente para Evolution API."""
import re
import time
from typing import Optional, Dict, Any

import requests
from loguru import logger

from config.settings import (
    EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE_NAME
)


class EvolutionAPI:
    """Cliente para interactuar con Evolution API."""

    def __init__(self):
        self.base_url = EVOLUTION_API_URL.rstrip("/")
        self.api_key = EVOLUTION_API_KEY
        self.instance_name = EVOLUTION_INSTANCE_NAME
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json",
        }

    @staticmethod
    def _normalizar_telefono(telefono: str) -> str:
        numero = re.sub(r"\D", "", telefono or "")
        if numero.startswith("00"):
            numero = numero[2:]
        if len(numero) == 10 and numero.startswith("3"):
            return f"57{numero}"
        return numero

    def send_message(self, telefono: str, mensaje: str, max_intentos: int = 3) -> bool:
        """Envía un mensaje de texto por WhatsApp."""
        url = f"{self.base_url}/message/sendText/{self.instance_name}"
        telefono = self._normalizar_telefono(telefono)

        payload = {
            "number": telefono,
            "text": mensaje,
        }

        for intento in range(1, max_intentos + 1):
            try:
                response = requests.post(url, json=payload, headers=self.headers, timeout=15)

                es_transitorio = response.status_code == 429 or response.status_code >= 500
                if es_transitorio and intento < max_intentos:
                    espera = 2 ** intento
                    logger.warning(
                        "Evolution API respondió {} (intento {}/{}). Reintentando en {}s...",
                        response.status_code, intento, max_intentos, espera
                    )
                    time.sleep(espera)
                    continue

                if 400 <= response.status_code < 500:
                    logger.error(
                        "Evolution API rechazó: status={} body={}",
                        response.status_code, response.text[:500]
                    )
                    return False

                response.raise_for_status()
                logger.info("Mensaje enviado a {}", telefono)
                return True
            except requests.exceptions.RequestException as e:
                if intento < max_intentos:
                    espera = 2 ** intento
                    logger.warning(
                        "Error enviando a {} (intento {}/{}): {}. Reintentando en {}s...",
                        telefono, intento, max_intentos, e, espera
                    )
                    time.sleep(espera)
                    continue
                logger.error("Error enviando a {}: {}", telefono, e)
                return False

        return False

    def get_instance_status(self) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/instance/connectionState/{self.instance_name}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error("Error obteniendo estado de instancia: {}", e)
            return None

    def get_qr_code(self) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/instance/connect/{self.instance_name}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error("Error obteniendo QR: {}", e)
            return None
