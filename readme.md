
<p align="center">
  <img
    src="https://github.com/user-attachments/assets/7e550d78-2c6f-40e9-afb8-219fb1d3e89e"
    alt="My Logo"
    width="500"    <!-- optional: control the display size -->
  />
</p>

# Laura AI Cold-Calling Agent — Technical Specification

## Overview

Laura is an AI-powered outbound calling agent designed to automate sales or outreach calls. The system integrates with Airtable for lead management, uses VAPI (and optionally Twilio) for telephony, and logs call outcomes to Airtable. It is built with Python, Flask, and is designed for deployment in Kubernetes environments.

---

## Architecture

- **app/main.py**: Entry point, Flask app, orchestrates call flow, exposes health and webhook endpoints.
- **app/leads.py**: LeadLoader class for fetching/updating leads from Airtable.
- **app/logger.py**: Logger class for logging call results to Airtable.
- **app/vapi_client.py**: Handles outbound call initiation via VAPI.
- **app/config.py**: Centralized configuration, loads from environment variables.
- **k8s/**: Kubernetes deployment and service manifests.
- **tests/**: Unit and integration tests.
- **Dockerfile**: Containerization for deployment.

---

## Features

### 1. Lead List Management (Airtable)
- **Source**: Airtable table (configurable).
- **LeadLoader**:
  - Fetches the next available lead (not "called" or "in progress").
  - Marks leads as "in progress" before calling, "called" after.
  - Optionally supports retry logic for failed calls.
- **Configurable fields**: Table name, API key, base ID.

### 2. Call Flow Orchestration
- Loads assistant prompt and persona from config.
- Fetches a lead, marks as "in progress", initiates call via VAPI.
- After call, marks lead as "called" and logs result.

### 3. Webhook Endpoints (Flask)
- **/health**: GET, returns "OK" for Kubernetes health checks.
- **/vapi-webhook**: POST, receives call status and summary from VAPI.
- **/twilio-status**: POST, receives call status from Twilio.
- **Security**: Endpoints require a secret token via header or query param.

### 4. Logging
- All call outcomes are logged to Airtable via Logger.
- Fields: Timestamp, AgentName, CustomerNumber, CallStatus, ConversationSummary, CallRecordingURL, NextAction.

### 5. Configuration
- All secrets and config are loaded from environment variables (see below).
- Support for .env files in development (python-dotenv recommended).
- Kubernetes secrets for production.

---

## Configuration & Environment Variables

| Variable                  | Description                                 | Example/Default         |
|---------------------------|---------------------------------------------|-------------------------|
| AIRTABLE_API_KEY          | Airtable API key                            | (secret)                |
| AIRTABLE_BASE_ID          | Airtable base ID                            | (secret)                |
| AIRTABLE_LEADS_TABLE      | Airtable table for leads                    | Leads                   |
| AIRTABLE_TABLE_NAME       | Airtable table for call logs                | Calls                   |
| VAPI_API_TOKEN            | VAPI API token                              | (secret)                |
| VAPI_PHONE_ID             | VAPI phone ID to use for outbound calls     | (secret)                |
| AGENT_NAME                | Name/persona of the AI agent                | Laura                   |
| AGENT_VOICE               | Voice model for calls                       | (e.g., "en-US-Wavenet-F")|
| WEBHOOK_SECRET            | Secret token for securing webhooks          | (secret)                |

- For local development, use a `.env` file.
- For Kubernetes, use `Secret` resources and reference them in deployment manifests.

---

## API Endpoints

### Health Check
- `GET /health`  
  Returns: `OK` (200)

### VAPI Webhook
- `POST /vapi-webhook`
- Auth: `X-Webhook-Token` header or `?token=...` query param
- Body: JSON payload from VAPI (call_id, status, summary, recording_url, customer_number, agent_name)
- Action: Logs call outcome to Airtable

### Twilio Status Webhook
- `POST /twilio-status`
- Auth: Same as above
- Body: JSON payload from Twilio (CallSid, CallStatus, To, RecordingUrl)
- Action: Logs call outcome to Airtable

---

## Outstanding Roadmap Items
Implement Lead List Management

✅ Decide on a lead source: Airtable

✅ Implement a loader in main.py (and leads.py) to fetch the next lead to call

✅ Mark leads as "called" or "in progress" to avoid duplicates

⬜ Optionally, support retry logic for failed calls (e.g., no answer) — Not yet implemented

Handle Webhooks for Call Status and Summaries

✅ Implement HTTP endpoints (/vapi-webhook, /twilio-status) using Flask in main.py

✅ Parse incoming webhook data to update call status, log outcomes, and store call recordings or transcripts

✅ Secure webhook endpoints (with a secret token)

Enhance Error Handling and Resilience

⬜ Add retries with exponential backoff for VAPI and Airtable API calls

⬜ Log all exceptions and errors with enough detail for debugging

⬜ Implement circuit breaker logic if repeated failures occur

Parameterize and Secure Configuration

⬜ Support loading config from .env files in development (using python-dotenv)

⬜ Document all required environment variables in a README.md or .env.example

⬜ For Kubernetes, ensure all secrets are referenced from K8s Secrets, not hardcoded

Improve LLM Prompt and Assistant Customization

⬜ Move prompt templates to a separate file or allow them to be passed as environment variables

⬜ Support dynamic prompt variables (e.g., customer name, product)

⬜ Allow voice selection via config

Testing and Mocking

⬜ Implement unit tests for all modules (vapi_client, logger, config validation, lead loader)

⬜ Use requests-mock or similar to mock external API calls in tests

⬜ Add integration tests for the full call flow (mocking VAPI and Airtable)

⬜ Set up a CI pipeline (e.g., GitHub Actions) to run tests on every commit

Build a Minimal UI/Dashboard (Optional but Recommended)

⬜ Implement a simple Flask or FastAPI web dashboard

⬜ Display recent calls, agent status, and allow pausing/resuming agents

⬜ Optionally, integrate with Kubernetes to scale deployments from the UI

Productionize Docker and Kubernetes Manifests

⬜ Finalize the Dockerfile (multi-stage build, non-root user, etc.)

⬜ Parameterize k8s/deployment.yaml for different agents/campaigns

⬜ Add resource requests/limits and health/readiness probes

⬜ Create and document K8s Secrets for all sensitive config

Monitoring, Logging, and Alerting

⬜ Integrate with a log aggregator (e.g., ELK, CloudWatch, GCP Logging)

⬜ Expose Prometheus metrics (calls made, errors, etc.) if possible

⬜ Set up alerts for high error rates, pod restarts, or API failures

Compliance and Consent Safeguards

⬜ Add logic to check that each lead has documented consent before calling

⬜ Ensure the agent’s first message includes required disclosures (recording, opt-out)

⬜ Log consent status and opt-outs in Airtable or your CRM

Documentation and Developer Onboarding

⬜ Write a comprehensive README.md covering setup, config, deployment, and troubleshooting

⬜ Document the API endpoints, environment variables, and expected webhook payloads

⬜ Provide example manifests and test data

(Optional) Integrate Lindy or Other Summarization/Automation

⬜ Add code or Make.com/Zapier integration to send call recordings/transcripts to Lindy

⬜ Store Lindy’s summaries and next actions in Airtable or notify sales reps

Legend:

✅ Complete

⬜ Still needs to be completed
### Error Handling & Resilience
- Add retries with exponential backoff for all external API calls (Airtable, VAPI).
- Log all exceptions with stack traces.
- Implement circuit breaker logic to pause calling after repeated failures.

### Configuration Improvements
- Add python-dotenv for local config loading.
- Document all environment variables in README.md or .env.example.
- Ensure all secrets are managed via Kubernetes Secrets in production.

### LLM Prompt Customization
- Move prompt templates to a separate file or allow override via environment variables.
- Support dynamic prompt variables (e.g., customer name, product).
- Allow voice selection via config.

### Testing & CI
- Implement unit tests for all modules (vapi_client, logger, config, lead loader).
- Use requests-mock or similar for external API mocking.
- Add integration tests for the full call flow.
- Set up CI (e.g., GitHub Actions) to run tests on every commit.

### UI/Dashboard (Optional)
- Build a minimal Flask or FastAPI dashboard to monitor calls, agent status, and control agent state.

### Productionization
- Finalize Dockerfile (multi-stage, non-root user).
- Parameterize k8s manifests for different agents/campaigns.
- Add resource requests/limits, health/readiness probes.
- Document and manage all secrets.

### Monitoring & Alerting
- Integrate with a log aggregator (ELK, CloudWatch, GCP Logging).
- Expose Prometheus metrics if possible.
- Set up alerts for high error rates, pod restarts, or API failures.

### Compliance & Consent
- Add logic to check for documented consent before calling.
- Ensure agent’s first message includes required disclosures.
- Log consent status and opt-outs.

### Documentation
- Write a comprehensive README.md.
- Document API endpoints, environment variables, and webhook payloads.
- Provide example manifests and test data.

### (Optional) Summarization/Automation
- Integrate with Lindy or similar for post-call summaries and automation.

---

## Development Conventions

- Use environment variables for all secrets and config.
- Keep all API keys and tokens out of source control.
- Use type hints and docstrings for all public functions.
- Write tests for all new features.
- Follow PEP8 for Python code style.

---

## Getting Started

1. Clone the repo and install dependencies (`pip install -r requirements.txt`).
2. Set up a `.env` file with all required variables.
3. Run the Flask app (`python app/main.py` or via WSGI/gunicorn for production).
4. Deploy to Kubernetes using the provided manifests, ensuring all secrets are set up.

---

## Contact

For questions or contributions, please contact @kjacked.
