FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    espeak-ng \
    espeak-ng-data \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
COPY ../src/piper /app/piper

EXPOSE 8000

CMD ["uvicorn", "piper_runtime:app", "--host", "0.0.0.0", "--port", "8000"]