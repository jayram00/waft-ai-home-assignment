FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential poppler-utils tesseract-ocr libmagic1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
