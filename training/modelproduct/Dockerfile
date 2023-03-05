FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential \
    && pip install --no-cache-dir --upgrade pip

WORKDIR /home/app
COPY ./requirements.txt /home/app
RUN pip install --no-cache-dir --requirement /home/app/requirements.txt
COPY . /home/app
ENV MODULE_NAME=finlytik_model

EXPOSE 3200

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "3200"]
