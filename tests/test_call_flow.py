# test_call_flow.py
# Tests for VAPI call flow using requests-mock

import pytest
import requests
from app.vapi_client import VAPIClient

def test_initiate_call_success(requests_mock):
    api_token = "test-token"
    phone_id = "test-phone-id"
    customer_number = "+1234567890"
    assistant_payload = {"firstMessage": "Hello!"}

    vapi = VAPIClient(api_token)
    url = f"{vapi.base_url}/call/phone"
    mock_response = {"callId": "abc123"}
    requests_mock.post(url, status_code=201, json=mock_response)

    result = vapi.initiate_call(phone_id, customer_number, assistant_payload)
    assert result["callId"] == "abc123"

def test_initiate_call_failure(requests_mock):
    api_token = "test-token"
    phone_id = "test-phone-id"
    customer_number = "+1234567890"
    assistant_payload = {"firstMessage": "Hello!"}

    vapi = VAPIClient(api_token)
    url = f"{vapi.base_url}/call/phone"
    requests_mock.post(url, status_code=400, json={"error": "Bad Request"})

    result = vapi.initiate_call(phone_id, customer_number, assistant_payload)
    assert result is None