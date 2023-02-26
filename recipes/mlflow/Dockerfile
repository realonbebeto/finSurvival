#### Custom mlflow server image
FROM python:3.10-slim

WORKDIR /home/app

# Install python packages

RUN pip install mlflow psycopg2-binary

COPY mlflow-repo /home/app/mlflow-repo

ENV DATABASE_PATH="sqlite:///mlruns.db"
ENV ARTIFACT_PATH="/home/app/mlflow-repo"
ENV PORT=5000

EXPOSE $PORT

CMD ["sh", "-c", "mlflow server --backend-store-uri $DATABASE_PATH --default-artifact-root $ARTIFACT_PATH --serve-artifacts --artifacts-destination $ARTIFACT_PATH --host 0.0.0.0 --port $PORT"]