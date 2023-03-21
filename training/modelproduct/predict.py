from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any
from pysurvival.utils import load_model
import joblib


class Details(BaseModel):
    age: float
    annual_income: float
    monthly_inhand_salary: float
    num_bank_accounts: float
    num_credit_card: float
    interest_rate: float
    num_of_loan: float
    num_of_delayed_payment: float
    changed_credit_limit: float
    num_credit_inquiries: float
    credit_mix: str
    outstanding_debt: float
    credit_utilization_ratio: float
    credit_history_age: float
    payment_of_min_amount: str
    total_emi_per_month: float
    amount_invested_monthly: float
    payment_behaviour: str
    monthly_balance: float


predict = APIRouter()
model = None
pipeline = None


@predict.on_event('startup')
async def loadModel():
    global pipeline
    global model
    pipeline = joblib.load('./data_pipe.sav')
    model = load_model('./model.zip')


@predict.post('/finlytik/predict',
              tags=["predictions"],
              description="Credit Risk Prediction")
async def getPrediction(details: Details):
    X = pipeline.transform([details.dict()])
    hazard = model.predict_hazard(X)
    survival = model.predict_survival(X)
    risk = model.predict_risk(X)
    return {"times": list(model.times),
            "hazard": list(hazard.flatten()),
            "risk": list(risk.flatten()),
            "survival": list(survival.flatten())}
