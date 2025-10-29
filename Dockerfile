FROM python:3.12-slim

WORKDIR /app

COPY app /app
COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y poppler-utils librsvg2-bin && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
CMD ["python", "main.py"]