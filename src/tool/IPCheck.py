import requests
import json
import logging
import os
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

@staticmethod
def check_ip_isp(ip_address: str) -> dict:
    """Controlla l'ISP di un indirizzo IP utilizzando l'API di AbuseIPDB."""
    logger.info("Controllo dell'ISP per l'indirizzo IP: %s", ip_address)
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
    return decodedResponse['data']["isp"]