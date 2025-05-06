# logger.py
# Handles logging call results to Airtable

import requests
from datetime import datetime
from app.config import Config

class Logger:
    def __init__(self, airtable_api_key=None, base_id=None, table_name="Calls"):
        self.airtable_api_key = airtable_api_key
        self.base_id = base_id
        self.table_name = table_name

    def log_call(self, result):
        """
        Log the call result to Airtable.
        result: dict with keys like customer_number, status, summary, agent_name, recording_url, next_action
        """
        if not self.airtable_api_key or not self.base_id:
            print("Airtable logging is disabled (missing config).")
            return

        endpoint = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"
        fields = {
            "Timestamp": datetime.utcnow().isoformat(),
            "AgentName": result.get("agent_name", Config.AGENT_NAME),
            "CustomerNumber": result.get("customer_number"),
            "CallStatus": result.get("status"),
            "ConversationSummary": result.get("summary")
        }
        if result.get("recording_url"):
            fields["CallRecordingURL"] = result["recording_url"]
        if result.get("next_action"):
            fields["NextAction"] = result["next_action"]

        headers = {
            "Authorization": f"Bearer {self.airtable_api_key}",
            "Content-Type": "application/json"
        }
        data = {"fields": fields}
        try:
            resp = requests.post(endpoint, json=data, headers=headers, timeout=10)
            if resp.status_code in (200, 201):
                print("Logged call to Airtable successfully.")
            else:
                print(f"Failed to log call: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"Exception during Airtable logging: {e}")