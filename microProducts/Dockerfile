FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential default-libmysqlclient-dev pkg-config && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove build-essential pkg-config && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 5003
CMD ["python", "run.py"]