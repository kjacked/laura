# test_logging.py
# Tests for Logger (Airtable logging) using requests-mock

import pytest
import requests
from app.logger import Logger

def test_log_call_success(requests_mock):
    api_key = "test-api-key"
    base_id = "test-base-id"
    table_name = "Calls"
    logger = Logger(api_key, base_id, table_name)

    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    requests_mock.post(url, status_code=201, json={"id": "rec123"})

    result = {
        "customer_number": "+1234567890",
        "agent_name": "TestAgent",
        "status": "Completed",
        "summary": "Test call summary",
        "recording_url": "https://example.com/rec.mp3"
    }

    # Should not raise and should log success
    logger.log_call(result)

def test_log_call_failure(requests_mock, caplog):
    api_key = "test-api-key"
    base_id = "test-base-id"
    table_name = "Calls"
    logger = Logger(api_key, base_id, table_name)

    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    requests_mock.post(url, status_code=400, json={"error": "Bad Request"})

    result = {
        "customer_number": "+1234567890",
        "agent_name": "TestAgent",
        "status": "Failed",
        "summary": "Test call summary"
    }

    with caplog.at_level("ERROR"):
        logger.log_call(result)
        assert "Failed to log call" in caplog.text