FROM python:3.10-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential \
    && pip install --no-cache-dir --upgrade pip

WORKDIR /home/auth
COPY ./requirements.txt /home/auth/
RUN pip install --no-cache-dir --requirement /home/auth/requirements.txt
COPY . /home/auth

EXPOSE 3000

CMD ["sh", "-c", "uvicorn auth.main:app --host 0.0.0.0 --port 3000"]