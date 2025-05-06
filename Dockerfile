# Dockerfile for Laura AI cold-calling agent

FROM python:3.11-slim

# Install system dependencies (uncomment if using VAPI Python SDK)
# RUN apt-get update && apt-get install -y portaudio19-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY app/main.py ./

ENV PORT=5000
ENV VAPI_API_TOKEN=""
ENV VAPI_PHONE_ID=""
ENV OPENAI_API_KEY=""
ENV AIRTABLE_API_KEY=""
ENV AIRTABLE_BASE_ID=""
ENV AIRTABLE_TABLE_NAME="CallsLog"

EXPOSE 5000

CMD ["python", "-u", "main.py"]