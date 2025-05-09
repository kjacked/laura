# vapi_client.py
# Handles interaction with VAPI (Voice API) for call initiation and management

import logging
from app.leads import retry_with_backoff
import requests

class VAPIClient:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.vapi.ai"

    @retry_with_backoff(max_attempts=3, initial_delay=1, backoff_factor=2)
    def initiate_call(self, phone_id, customer_number, assistant_payload):
        """
        Initiate an outbound call via VAPI.
        """
        url = f"{self.base_url}/call/phone"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "assistant": assistant_payload,
            "phoneNumberId": phone_id,
            "customer": {"number": customer_number}
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=15)
            if resp.status_code == 201:
                data = resp.json()
                logging.info(f"Call initiated successfully. Call ID: {data.get('callId')}")
                return data
            else:
                logging.error(f"Failed to initiate call: {resp.status_code} - {resp.text}")
                return None
        except Exception as e:
            logging.exception(f"Exception during VAPI call initiation: {e}")
            return None