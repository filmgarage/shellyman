ARG BUILD_FROM
FROM ${BUILD_FROM}

ENV LANG=C.UTF-8     PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

RUN apk add --no-cache python3 py3-pip ca-certificates curl bash

WORKDIR /app
COPY requirements.txt /app/

# Use a venv to avoid PEP 668 (externally-managed environment) issues
RUN python3 -m venv /venv  && /venv/bin/python -m pip install --no-cache-dir --upgrade pip setuptools wheel  && /venv/bin/pip install --no-cache-dir -r requirements.txt

# App code
COPY app/ /app/
COPY static/ /app/static/
COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD [ "/run.sh" ]
