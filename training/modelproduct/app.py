from fastapi import FastAPI
from predict import predict
import warnings
with warnings.catch_warnings():
    warnings.simplefilter(action='ignore', category=FutureWarning)


app = FastAPI(title="Finlytik ML API",
              description="API for Credit Risk", version="1.0")

app.include_router(predict, prefix='/v1')
