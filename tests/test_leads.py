# test_leads.py
# Tests for LeadLoader (Airtable lead management) using requests-mock

import pytest
import requests
from app.leads import LeadLoader

def test_get_next_lead_success(requests_mock):
    api_key = "test-api-key"
    base_id = "test-base-id"
    table_name = "Leads"
    loader = LeadLoader(api_key, base_id, table_name)

    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    mock_record = {
        "id": "rec123",
        "fields": {
            "Phone": "+1234567890",
            "Status": "new"
        }
    }
    requests_mock.get(url, status_code=200, json={"records": [mock_record]})

    lead = loader.get_next_lead()
    assert lead["id"] == "rec123"
    assert lead["Phone"] == "+1234567890"

def test_get_next_lead_none(requests_mock):
    api_key = "test-api-key"
    base_id = "test-base-id"
    table_name = "Leads"
    loader = LeadLoader(api_key, base_id, table_name)

    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    requests_mock.get(url, status_code=200, json={"records": []})

    lead = loader.get_next_lead()
    assert lead is None

def test_mark_lead_status_success(requests_mock):
    api_key = "test-api-key"
    base_id = "test-base-id"
    table_name = "Leads"
    loader = LeadLoader(api_key, base_id, table_name)

    record_id = "rec123"
    url = f"https://api.airtable.com/v0/{base_id}/{table_name}/{record_id}"
    requests_mock.patch(url, status_code=200, json={"id": record_id, "fields": {"Status": "called"}})

    resp = loader.mark_lead_status(record_id, "called")
    assert resp["id"] == record_id
    assert resp["fields"]["Status"] == "called"