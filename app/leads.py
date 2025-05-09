import time
import logging
from functools import wraps

def retry_with_backoff(max_attempts=3, initial_delay=1, backoff_factor=2):
    """
    Decorator for retrying a function with exponential backoff.
    Logs exceptions and raises after max_attempts.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.exception(f"Attempt {attempt} failed: {e}")
                    if attempt == max_attempts:
                        raise
                    time.sleep(delay)
                    delay *= backoff_factor
        return wrapper
    return decorator
# leads.py
# Handles fetching and updating leads from Airtable

import requests
from app.config import Config

class LeadLoader:
    def __init__(self, airtable_api_key=None, base_id=None, table_name="Leads"):
        self.airtable_api_key = airtable_api_key or Config.AIRTABLE_API_KEY
        self.base_id = base_id or Config.AIRTABLE_BASE_ID
        self.table_name = table_name or Config.AIRTABLE_LEADS_TABLE
        self.endpoint = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"
        self.headers = {
            "Authorization": f"Bearer {self.airtable_api_key}",
            "Content-Type": "application/json"
        }

    @retry_with_backoff(max_attempts=3, initial_delay=1, backoff_factor=2)
    def get_next_lead(self):
        """
        Fetch the next lead that is not 'called' or 'in progress'.
        Returns a dict with lead fields and Airtable record ID.
        """
        params = {
            "filterByFormula": "AND({Status} != 'called', {Status} != 'in progress')",
            "maxRecords": 1
        }
        resp = requests.get(self.endpoint, headers=self.headers, params=params)
        resp.raise_for_status()
        records = resp.json().get("records", [])
        if not records:
            return None
        record = records[0]
        lead = record["fields"]
        lead["id"] = record["id"]
        return lead

    @retry_with_backoff(max_attempts=3, initial_delay=1, backoff_factor=2)
    def mark_lead_status(self, record_id, status):
        """
        Update the status of a lead by record ID.
        """
        url = f"{self.endpoint}/{record_id}"
        data = {"fields": {"Status": status}}
        resp = requests.patch(url, headers=self.headers, json=data)
        resp.raise_for_status()
        return resp.json()

    def mark_lead_in_progress(self, record_id):
        return self.mark_lead_status(record_id, "in progress")

    def mark_lead_called(self, record_id):
        return self.mark_lead_status(record_id, "called")

    def retry_lead(self, record_id):
        """
        Optionally reset the status for retry logic.
        """
        return self.mark_lead_status(record_id, "retry")