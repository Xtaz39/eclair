from typing import TypedDict

import requests

from django.conf import settings


class CheckResponse(TypedDict):
    success: bool
    challenge_ts: int  # ex: '2021-05-12T19:30:24Z'
    hostname: str
    score: float
    action: str


class ClientError(Exception):
    pass


class Client:
    def __init__(self, api_secret: str):
        self._http_client = requests.Session()
        self._api_secret = api_secret

    def check(self, user_response_token: str) -> bool:
        """https://developers.google.com/recaptcha/docs/verify"""
        params = {
            "secret": self._api_secret,
            "response": user_response_token,
            # "remoteip" # Optional. The user's IP address.
        }
        resp = self._http_client.post(
            url="https://www.google.com/recaptcha/api/siteverify",
            params=params,
            timeout=1.0,
        )

        if not resp.ok:
            raise ClientError(f"{resp.status_code}: {resp.text}")

        data: CheckResponse = resp.json()
        return data["score"] > 0.5


client = Client(settings.RECAPTCHA_API_KEY)
