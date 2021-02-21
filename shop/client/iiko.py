from dataclasses import dataclass
from typing import Any, List
from urllib.parse import urljoin

import requests
from django.conf import settings


class ClientError(Exception):
    pass


class Client:
    def __init__(self, url: str, login: str, password: str):
        self._url = url
        self._login = login
        self._password = password
        self._token = ""
        self._http_client = requests.Session()
        self._refresh_access_token()

    def _refresh_access_token(self):
        url = urljoin(self._url, "auth/access_token")
        resp = self._http_client.get(
            url,
            params={
                "user_id": self._login,
                "user_secret": self._password,
            },
        )
        if not resp.ok:
            raise ClientError(resp.text)

        self._token = resp.json()
        return

    def _send_get(self, endpoint: str, params: dict[Any, Any] = None) -> dict[Any, Any]:
        url = urljoin(self._url, endpoint)
        params = params or {}

        for _ in range(2):
            params["access_token"] = self._token
            resp = self._http_client.get(url, params=params)
            if not resp.ok:
                # refresh token and retry
                self._refresh_access_token()
            else:
                break

        if not resp.ok:
            raise ClientError(resp.text)

        data = resp.json()
        return data

    def list_organisations(self):
        return self._send_get("organization/list")

    def get_stop_list(self, organization_id: str) -> "List[StopListAtOrganization]":
        data = self._send_get(
            "stopLists/getDeliveryStopList", params={"organization": organization_id}
        )

        stop_lists = []
        for lst in data["stopList"]:
            stop_list = StopListAtOrganization(
                organizationId=lst["organizationId"],
                terminalId=lst["terminalID"],
                items=[
                    StopListItem(productId=item["productId"], balance=lst["balance"])
                    for item in lst["items"]
                ],
            )

            stop_lists.append(stop_list)

        return stop_lists

    def get_nomenclature(self, organization_id: str) -> "Nomenclature":
        data = self._send_get(f"nomenclature/{organization_id}")

        products = [
            Product(
                id=p["id"], name=p["name"], code=p["code"], description=p["description"]
            )
            for p in data["products"]
        ]
        nomenclature = Nomenclature(
            products=products,
            revision=data["revision"],
        )

        return nomenclature


@dataclass
class Product:
    """
    https://docs.google.com/document/d/1pRQNIn46GH1LVqzBUY5TdIIUuSCOl-A_xeCBbogd2bE/edit#bookmark=kix.a2rirkw3zehc
    """

    id: str
    name: str
    code: str  # артикул
    description: str
    ...


@dataclass
class Nomenclature:
    """
    https://docs.google.com/document/d/1pRQNIn46GH1LVqzBUY5TdIIUuSCOl-A_xeCBbogd2bE/edit#bookmark=kix.tll8jvhgmwmu
    """

    products: List[Product]
    revision: int
    ...


@dataclass
class StopListItem:
    """
    https://docs.google.com/document/d/1pRQNIn46GH1LVqzBUY5TdIIUuSCOl-A_xeCBbogd2bE/edit#bookmark=kix.ipqrdjto1cez
    """

    productId: str
    balance: int


@dataclass
class StopListAtOrganization:
    """
    https://docs.google.com/document/d/1pRQNIn46GH1LVqzBUY5TdIIUuSCOl-A_xeCBbogd2bE/edit#bookmark=kix.511l6n1v5hbv
    """

    organizationId: str
    terminalId: str
    items: List[StopListItem]


client = Client(settings.IIKO_URL, settings.IIKO_LOGIN, settings.IIKO_PASSWORD)
