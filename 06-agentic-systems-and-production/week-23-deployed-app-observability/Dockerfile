FROM python:3.12-slim

WORKDIR /app

# Install dependencies first to leverage Docker layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8000

# ANTHROPIC_API_KEY is provided at runtime, e.g.:
#   docker run -e ANTHROPIC_API_KEY=sk-ant-... -p 8000:8000 summarize-service
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
