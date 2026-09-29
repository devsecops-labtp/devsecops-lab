FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
 && apt-get update && apt-get install -y --no-install-recommends iputils-ping \
 && rm -rf /var/lib/apt/lists/*
COPY app.py .
RUN useradd -m app && chown -R app /app
USER app
EXPOSE 5000
CMD ["python", "app.py"]
