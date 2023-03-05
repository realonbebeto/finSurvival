from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from gateway import crud, models, schemas
from gateway.api import deps
import pika
import json

router = APIRouter()
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()


@router.post("/infer")
def inference(*, profile_in: schemas.ProfileCreate,
              db: Session = Depends(deps.getDb),
              current_user: models.User = Depends(deps.getCurrentActiveUser)):
    current_user_data = jsonable_encoder(current_user)
    profile_in.email = current_user_data.email
    try:
        profile = crud.profile.create(db, obj_in=profile_in)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

    message = {
        "profile_id": str(profile.id),
        "username": profile.email
    }

    try:
        channel.basic_publish(exchange="",
                              routing_key="detail",
                              body=json.dumps(message),
                              properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE))
    except Exception as e:
        crud.profile.delete(db, profile.id)
        raise HTTPException(status_code=500, detail=e)


@router.get("/infer", response_model=List[schemas.Profile])
def viewReports(db: Depends(deps.getDb),
                skip: int = 0,
                limit: int = 100,
                current_user: models.User = Depends(deps.getCurrentActiveUser)):

    profiles = crud.profile.getMultiByEmail(
        db, email=current_user.email, skip=skip, limit=limit)
    return profiles
