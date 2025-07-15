FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY test_client.py .

CMD ["sh", "-c", "pytest test_client.py -v --tb=short 2>&1 | tee /app/logs/pytest_trace.log"]