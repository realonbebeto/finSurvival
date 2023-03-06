FROM python:3.10-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential \
    && pip install --no-cache-dir --upgrade pip

WORKDIR /home/notification
COPY ./requirements.txt /home/notification//
RUN pip install --no-cache-dir --requirement /home/notification/requirements.txt
COPY . /home/notification/

EXPOSE 3000

CMD CMD ["python3", "notification/consumer.py"]