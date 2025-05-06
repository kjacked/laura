# config.py
# Loads configuration from environment variables

import os

class Config:
    VAPI_API_TOKEN = os.getenv("VAPI_API_TOKEN")
    VAPI_PHONE_ID = os.getenv("VAPI_PHONE_ID")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
    AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
    AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "Calls")
    AGENT_VOICE = os.getenv("AGENT_VOICE", "jennifer-playht")
    AGENT_NAME = os.getenv("AGENT_NAME", "Laura")
    LINDY_API_KEY = os.getenv("LINDY_API_KEY")

    @staticmethod
    def validate():
        required = ["VAPI_API_TOKEN", "VAPI_PHONE_ID"]
        for var in required:
            if not getattr(Config, var):
                raise EnvironmentError(f"Missing required config: {var}")