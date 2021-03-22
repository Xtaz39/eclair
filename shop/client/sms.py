import requests
from django.conf import settings


class ClientError(Exception):
    pass


class Client:
    def __init__(self, api_key=str, debug_mode=True):
        self._http_client = requests.Session()
        self._api_id = api_key
        self._debug_mode = debug_mode

    def send_sms(self, text: str, to: str, user_ip=""):
        params = {
            "api_id": self._api_id,
            "json": 1,
            "msg": text,
            "to": to,
            "ttl": 2,  # minutes
        }
        if user_ip:
            params["ip"] = user_ip
        if self._debug_mode:
            params["test"] = "1"

        resp = self._http_client.get(
            url="https://sms.ru/sms/send",
            params=params,
            timeout=1.0,
        )

        if not resp.ok:
            raise ClientError(f"{resp.status_code}: {resp.text}")

        data = resp.json()
        if data["status"] != "OK" or any(
            s["status"] != "OK" for s in data["sms"].values()
        ):
            raise ClientError(f"Response not OK: {data}")

        return


client = Client(settings.SMS_API_KEY, debug_mode=settings.DEBUG)
