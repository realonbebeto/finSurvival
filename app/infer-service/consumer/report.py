import pika
import json
import os
from consumer import schemas
import requests
from fastapi.encoders import jsonable_encoder
from consumer.core.config import settings


def model_fields(obj_in: schemas.ProfileModel):
    obj_in = obj_in.dict()
    obj_in.pop("email")
    obj_in = schemas.ProfileModel(**obj_in)
    return obj_in


def start(message, db, crud, channel):
    message = json.loads(message)

    # fetch from db profile contents
    # TODO: clear type conversions here from db profile to Details pydantic model
    current_profile = crud.profile.getByID(db, id=message["profile_id"])
    model_data = model_fields(current_profile)
    profile_in = schemas.ProfileUpdate(**jsonable_encoder(current_profile))
    # Infer
    response = requests.post(
        f"http://{settings.MODEL_ADDRESS}/finlytik/predict", details=model_data)

    if response.status_code == 200:
        profile_in.times = response.json()['times']
        profile_in.hazard_score = response.json()['hazard_score']
        profile_in.risk_score = response.json()['risk_score']
        profile_in.survival_score = response.json()['survival_score']
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
        return "failed to publish message"
