import json
from typing import Any, List

import pika
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from gateway import crud, models, schemas
from gateway.api import deps

router = APIRouter()
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()


@router.post("/infer")
def inference(
    *,
    profile_in: schemas.ProfileCreate,
    db: Session = Depends(deps.getDb),
    current_user: models.User = Depends(deps.getCurrentActiveUser)
):
    current_user_data = jsonable_encoder(current_user)
    profile_in.email = current_user_data['email']

    try:
        profile = crud.profile.create(db, obj_in=profile_in)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

    message = {
        "profile_id": str(profile.id),
        "username": profile.email,
        "processed": False,
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key="detail",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as e:
        crud.profile.delete(db=db, id=profile.id)
        raise HTTPException(
            status_code=500, detail="Error with publishing message on the RabbitMQ detail queue")


@router.get("/reports", response_model=List[schemas.ProfileReport])
def view_reports(
    db: Session = Depends(deps.getDb),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.getCurrentActiveUser),
):
    profiles = crud.profile.getMultiByEmail(
        db, email=current_user.email, skip=skip, limit=limit
    )
    return profiles
