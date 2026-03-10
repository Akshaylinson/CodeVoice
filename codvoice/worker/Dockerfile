FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    espeak-ng \
    espeak-ng-data \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "tts_worker.py"]