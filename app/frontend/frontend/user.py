import requests
from core.config import settings


def login(username: str, password: str) -> bool:
    if (username is None):
        return False
    try:
        basic_auth = {'username': username,
                      'password': password}
        response = requests.post(
            f"http://{settings.GATEWAY_SVC_ADDRESS}/login", data=basic_auth)

        if response.status_code == 200:
            return 200, response.json()['access_token']
        else:
            return 401, "Unauthorized"
    except:
        return None, None
