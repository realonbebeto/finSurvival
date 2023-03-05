import json
import os

import pika
import requests
import uvicorn
from fastapi import Depends, FastAPI, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from pydantic import BaseModel

from database import get_db
from models import Profile


class Detail(BaseModel):
    income: int
    cred_history: int


class UsernamePasswordForm(BaseModel):
    username: str
    password: str

app = FastAPI(title='Gateway')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

@app.post("/login")
def login(user_cred: OAuth2PasswordRequestForm = Depends()):

    basicAuth = (user_cred.username, user_cred.password)

    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login", auth=basicAuth
    )
    if response.status_code == 200:
        return response.json()
    else:
        return response.json(), response.status_code
    

@app.post("/register")
def register(user: UsernamePasswordForm):
    basicAuth = (user.username, user.password)
    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/register", auth=basicAuth
    )

    if response.status_code == 200:
        return response.json()
    else:
        return response.json(), response.status_code


@app.post("/infer")
def inference(detail: Detail, request: Depends(Request), db: Depends(get_db)):

    if detail:
        try:
            detail.email = request.state.user_id
            new_details = Profile(**detail.dict())
            db.add(new_details)
            db.commit()
            db.refresh(new_details)
            detail_id = new_details.id
            username = new_details.email
        except Exception as e:
            return "Internal server error", 500, e

        message = {
                "detail_id": str(detail_id),
                "username": username
            }
        try:
            channel.basic_publish(exchange="",
                                  routing_key="detail",
                                  body=json.dumps(message),
                                  properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE))
        except Exception as e:
            profile = db.query(Profile).filter_by(id=detail_id).first()
            profile.delete(synchronize_session=False)
            db.commit()
            return "Internal server error", 500, e


@app.post("/infer")
def viewReports(request: Depends(Request), db: Depends(get_db)):
    detail_id = request.args.get("detail_id")
    if not detail_id:
            return "detail_id is required", 400
    try:
        risk_score = db.query(Profile.risk_score).filter(Profile.id == int(detail_id))
        hazard_score = db.query(Profile.hazard_score).filter(Profile.id == int(detail_id))
        survival_score = db.query(Profile.survival_score).filter(Profile.id == int(detail_id))
        return risk_score, hazard_score, survival_score
    except Exception as e:
        return "Internal server error", 500, e


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4040)