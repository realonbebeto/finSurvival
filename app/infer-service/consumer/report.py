import pika
import json
import os
from consumer import schemas
import requests
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from consumer.core.config import settings


def start(message, db, crud, channel):
    message = json.loads(message)

    # fetch from db profile contents
    # TODO: clear type conversions here from db profile to Details pydantic model
    current_profile = crud.profile.getByID(db, id=message["profile_id"])
    current_profile_data = jsonable_encoder(current_profile)
    model_data = schemas.ProfileModel(
        age=current_profile_data['age'],
        email=current_profile_data['email'],
        annual_income=current_profile_data['annual_income'],
        monthly_inhand_salary=current_profile_data['monthly_inhand_salary'],
        num_bank_accounts=current_profile_data['num_bank_accounts'],
        num_credit_card=current_profile_data['num_credit_card'],
        interest_rate=current_profile_data['interest_rate'],
        num_of_loan=current_profile_data['num_of_loan'],
        num_of_delayed_payment=current_profile_data['num_of_delayed_payment'],
        changed_credit_limit=current_profile_data['changed_credit_limit'],
        num_credit_inquiries=current_profile_data['num_credit_inquiries'],
        credit_mix=current_profile_data['credit_mix'],
        outstanding_debt=current_profile_data['outstanding_debt'],
        credit_utilization_ratio=current_profile_data['credit_utilization_ratio'],
        credit_history_age=current_profile_data['credit_history_age'],
        payment_of_min_amount=current_profile_data['payment_of_min_amount'],
        total_emi_per_month=current_profile_data['total_emi_per_month'],
        amount_invested_monthly=current_profile_data['amount_invested_monthly'],
        payment_behaviour=current_profile_data['payment_behaviour'],
        monthly_balance=current_profile_data['monthly_balance'],
    )
    profile_in = schemas.ProfileUpdate(**current_profile_data)

    # Infer
    response = requests.post(
        f"http://{settings.MODEL_ADDRESS}:3200/v1/finlytik/predict", json=model_data.dict())

    if response.status_code == 200:
        profile_in.times = response.json()['times']
        profile_in.hazard_score = response.json()['hazard']
        profile_in.risk_score = response.json()['risk']
        profile_in.survival_score = response.json()['survival']
        crud.profile.update(db, db_obj=current_profile, obj_in=profile_in)
        message["processed"] = True

    try:
        channel.basic_publish(
            exchange="",
            routing_key=settings.PROFILE_QUEUE,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err:
        raise HTTPException(
            status_code=500, detail="Error with publishing message on the RabbitMQ profile queue")
