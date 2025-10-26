ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM $BUILD_FROM

ENV LANG=C.UTF-8         PYTHONDONTWRITEBYTECODE=1         PYTHONUNBUFFERED=1

# OS deps
RUN apk add --no-cache python3 py3-pip ca-certificates curl bash

# Python deps
WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

# App code
COPY app/ /app/
COPY static/ /app/static/
COPY run.sh /run.sh
RUN chmod +x /run.sh

# Ingress port is provided via $INGRESS_PORT. Fallback to 8099 in code.
CMD [ "/run.sh" ]
