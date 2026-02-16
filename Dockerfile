ARG BUILD_FROM=python:3.13-alpine
FROM ${BUILD_FROM}

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data

ENV CONFIG_PATH=/data/config.cfg

CMD ["python3", "run.py"]
