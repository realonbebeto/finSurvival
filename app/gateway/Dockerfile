FROM python:3.10-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential \
    && pip install --no-cache-dir --upgrade pip

WORKDIR /home/gateway
COPY ./requirements.txt /home/gateway/
RUN pip install --no-cache-dir --requirement /home/gateway/requirements.txt
COPY . /home/gateway/

EXPOSE 3100

CMD ["sh", "-c", "uvicorn gateway.main:app --host 0.0.0.0 --port 3100"]