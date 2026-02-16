FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache tini

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data

ENV CONFIG_PATH=/data/config.cfg
ENV PORT=5000

EXPOSE 5000

ENTRYPOINT ["tini", "--"]
CMD ["python", "run.py"]
