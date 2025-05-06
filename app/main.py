# main.py
# Entry point for Laura AI cold-calling agent

from app.config import Config
from app.vapi_client import VAPIClient
from app.logger import Logger
from flask import Flask

import sys

# Health check endpoint for Kubernetes
app = Flask(__name__)

@app.route("/health")
def health():
    return "OK", 200

# --- Webhook Endpoints ---

from flask import request, jsonify
import os

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", Config.WEBHOOK_SECRET if hasattr(Config, "WEBHOOK_SECRET") else None)

def check_webhook_auth():
    # Simple token-based auth (can be replaced with IP allowlist or more robust logic)
    token = request.headers.get("X-Webhook-Token") or request.args.get("token")
    if not WEBHOOK_SECRET or token != WEBHOOK_SECRET:
        return False
    return True

@app.route("/vapi-webhook", methods=["POST"])
def vapi_webhook():
    if not check_webhook_auth():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(force=True)
    # Example: update call status, log outcome, store recording/transcript
    # You may need to adjust field names based on VAPI's webhook payload
    call_id = data.get("call_id")
    status = data.get("status")
    summary = data.get("summary")
    recording_url = data.get("recording_url")
    customer_number = data.get("customer_number")
    agent_name = data.get("agent_name", Config.AGENT_NAME)
    # Log to Airtable
    logger = Logger(Config.AIRTABLE_API_KEY, Config.AIRTABLE_BASE_ID, Config.AIRTABLE_TABLE_NAME)
    logger.log_call({
        "customer_number": customer_number,
        "agent_name": agent_name,
        "status": status,
        "summary": summary,
        "recording_url": recording_url
    })
    return jsonify({"success": True}), 200

@app.route("/twilio-status", methods=["POST"])
def twilio_status():
    if not check_webhook_auth():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(force=True)
    # Example: parse Twilio status callback
    call_sid = data.get("CallSid")
    call_status = data.get("CallStatus")
    # Log or update call status as needed
    logger = Logger(Config.AIRTABLE_API_KEY, Config.AIRTABLE_BASE_ID, Config.AIRTABLE_TABLE_NAME)
    logger.log_call({
        "customer_number": data.get("To"),
        "agent_name": Config.AGENT_NAME,
        "status": call_status,
        "summary": f"Twilio call status: {call_status}",
        "recording_url": data.get("RecordingUrl")
    })
    return jsonify({"success": True}), 200
def main():
    try:
        Config.validate()
    except EnvironmentError as e:
        print(f"Config error: {e}")
        sys.exit(1)

    # Prepare assistant payload (LLM prompt)
    SYSTEM_PROMPT = (
        f"You are {Config.AGENT_NAME}, an AI sales assistant. "
        "You are calling potential customers. "
        "Your style is professional, friendly, and concise. "
        "Introduce yourself and the company, explain why you're calling, and engage the customer. "
        "If the customer is not interested, thank them and end. "
        "Keep each response under 2 sentences."
    )
    FIRST_MESSAGE = (
        f"Hello, this is {Config.AGENT_NAME}. How are you today?"
    )
    assistant_payload = {
        "firstMessage": FIRST_MESSAGE,
        "model": {
            "provider": "openai",
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ]
        },
        "voice": Config.AGENT_VOICE,
        "recordingEnabled": True,
        "interruptionsEnabled": False
    }

    # Instantiate clients
    vapi = VAPIClient(Config.VAPI_API_TOKEN)
    logger = Logger(Config.AIRTABLE_API_KEY, Config.AIRTABLE_BASE_ID, Config.AIRTABLE_TABLE_NAME)

    # Lead management integration
    from app.leads import LeadLoader
    lead_loader = LeadLoader(Config.AIRTABLE_API_KEY, Config.AIRTABLE_BASE_ID, getattr(Config, "AIRTABLE_LEADS_TABLE", "Leads"))
    lead = lead_loader.get_next_lead()
    if not lead or not lead.get("Phone"):
        print("No available leads to call.")
        return

    record_id = lead["id"]
    lead_phone_number = lead["Phone"]

    # Mark lead as in progress
    lead_loader.mark_lead_in_progress(record_id)

    # Initiate call
    print(f"Initiating call to {lead_phone_number} via VAPI...")
    vapi.initiate_call(Config.VAPI_PHONE_ID, lead_phone_number, assistant_payload)

    # Mark lead as called (in a real implementation, this should be after call completion)
    lead_loader.mark_lead_called(record_id)

    # Log result
    call_result = {
        "customer_number": lead_phone_number,
        "agent_name": Config.AGENT_NAME,
        "status": "Initiated",
        "summary": "Call initiated (lead management)"
    }
    logger.log_call(call_result)
    print("Call result logged.")

if __name__ == "__main__":
    import threading
    # Start health check endpoint in a separate thread
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(Config.PORT or 5000)), daemon=True).start()
    main()