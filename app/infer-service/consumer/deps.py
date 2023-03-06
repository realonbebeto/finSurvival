from typing import Generator
from consumer.db.session import SessionLocal


def getDb() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
