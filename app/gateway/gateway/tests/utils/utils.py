import random
import string
from typing import Dict

from auth.core.config import settings
from fastapi.testclient import TestClient


def randomLowerString() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def randomEmail() -> str:
    return f"{randomLowerString()}@{randomLowerString()}.com"


def get_superuser_token_headers(client: TestClient) -> Dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
