FROM python:3.10-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential \
    && pip install --no-cache-dir --upgrade pip

WORKDIR /home/frontend
COPY ./requirements.txt /home/frontend/
RUN pip install --no-cache-dir --requirement /home/frontend/requirements.txt
COPY . /home/frontend/

EXPOSE 3600

CMD ["sh", "-c", "streamlit run frontend/main.py --server.port 3600 --server.address 0.0.0.0"]