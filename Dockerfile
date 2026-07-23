FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 CONTROL_TOWER_HOME=/data
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && pip install --no-cache-dir ".[vision]"
EXPOSE 8000
CMD ["uvicorn","control_tower.api.app:app","--host","0.0.0.0","--port","8000"]
