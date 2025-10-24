import requests
import json
import logging
import os
from typing import Dict
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

IP_ISP_CACHE: Dict[str, str] = {}

@staticmethod
def check_ip_isp(ip_address: str) -> str:
    """Controlla l'ISP di un indirizzo IP utilizzando l'API di AbuseIPDB."""
    logger.info("Controllo dell'ISP per l'indirizzo IP: %s", ip_address)

    if is_checked(ip_address):  
        return IP_ISP_CACHE.get(ip_address)

    url = 'https://api.abuseipdb.com/api/v2/check'

    querystring = {
        'ipAddress': ip_address,
        'maxAgeInDays': '90'
    }

    headers = {
        'Accept': 'application/json',
        'Key': os.getenv("ABUSEL_API")
    }

    response = requests.request(method='GET', url=url, headers=headers, params=querystring)

    # Formatted output
    decodedResponse = json.loads(response.text)
    IP_ISP_CACHE[ip_address] = decodedResponse['data']["isp"]
    logger.debug("ISP salvato in cache per %s", ip_address)

    return decodedResponse['data']["isp"]


def is_checked(ip_address: str) -> str:
    """Restituisce l'ISP dell'IP sfruttando una cache in memoria per ridurre le chiamate all'API."""

    cached_isp = IP_ISP_CACHE.get(ip_address)
    if cached_isp is not None:
        logger.debug("ISP recuperato dalla cache per %s", ip_address)
        return True

    return False