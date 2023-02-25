FROM python:3.10-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential \
    && pip install --no-cache-dir --upgrade pip

WORKDIR /home/app
COPY ./requirements.txt /home/app
RUN pip install --no-cache-dir --requirement /home/app/requirements.txt
COPY . /home/app

EXPOSE 3000

CMD ["python3", "server.py"]