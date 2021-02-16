import enum
from dataclasses import dataclass
from typing import TypedDict
from urllib.parse import urljoin

import requests
from django.conf import settings


class ClientError(Exception):
    pass


class ClientOptions(TypedDict):
    integration_id: str
    secret_key: str
    access_token: str
    auth_code: str


class PaymentType(enum.Enum):
    CASH = 34113529
    CARD = 34113523


@dataclass
class Order:
    order_id: str
    total_amount: int
    payment_type: PaymentType
    content: str
    address: str


class Client:
    SITE_PIPELINE_ID = 3428449
    ROBOT_ID = 0

    def __init__(self, options: ClientOptions):
        self._url = "https://dennabiullin.amocrm.ru"
        self._access_token = options["access_token"]
        self._refresh_token = ""
        self._secret_key = options["secret_key"]
        self._integration_id = options["integration_id"]
        self._auth_code = options["auth_code"]
        self._http_client = requests.Session()

    def _obtain_access_token(self):
        """https://www.amocrm.ru/developers/content/oauth/step-by-step#get_access_token"""
        url = urljoin(self._url, "/oauth2/access_token")
        resp = self._http_client.post(
            url,
            data={
                "client_id": self._integration_id,
                "client_secret": self._secret_key,
                "grant_type": "authorization_code",
                "code": self._auth_code,
                "redirect_uri": "https://dmssk.github.io/",
            },
        )
        if not resp.ok:
            raise ClientError(resp.text)

        data = resp.json()
        self._access_token = data["access_token"]
        self._refresh_token = data["refresh_token"]
        return

    def _refresh_access_token(self):
        """https://www.amocrm.ru/developers/content/oauth/step-by-step#easy_auth"""
        url = urljoin(self._url, "/oauth2/access_token")
        resp = self._http_client.post(
            url,
            data={
                "client_id": self._integration_id,
                "client_secret": self._secret_key,
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
                "redirect_uri": "https://dmssk.github.io/",
            },
        )
        if not resp.ok:
            raise ClientError(resp.text)

        data = resp.json()
        self._access_token = data["access_token"]
        self._refresh_token = data["refresh_token"]
        return

    def get_leads(self):
        """https://www.amocrm.ru/developers/content/crm_platform/leads-api"""
        url = urljoin(self._url, "api/v4/leads")
        resp = self._http_client.get(
            url, headers={"Authorization": f"Bearer {self._access_token}"}
        )
        if not resp.ok:
            raise ClientError(resp.text)

        data = resp.json()
        return data

    def get_lead(self, id_: int):
        """https://www.amocrm.ru/developers/content/crm_platform/leads-api"""
        url = urljoin(self._url, f"api/v4/leads/{id_}")
        resp = self._http_client.get(
            url, headers={"Authorization": f"Bearer {self._access_token}"}
        )
        if not resp.ok:
            raise ClientError(resp.text)

        data = resp.json()
        return data

    def create_lead(self, contact_id: int, order: Order):
        """https://www.amocrm.ru/developers/content/crm_platform/leads-api"""
        url = urljoin(self._url, "api/v4/leads")
        product_field_id = 608539
        address_field_id = 608543

        resp = self._http_client.post(
            url,
            headers={"Authorization": f"Bearer {self._access_token}"},
            json=[
                {
                    "name": order.order_id,
                    "price": order.total_amount,
                    "pipeline_id": self.SITE_PIPELINE_ID,
                    "created_by": self.ROBOT_ID,
                    "status_id": order.payment_type,
                    # https://www.amocrm.ru/developers/content/crm_platform/custom-fields#cf-fill-examples
                    "custom_fields_values": [
                        {
                            "field_id": product_field_id,
                            "values": [{"value": order.content}],
                        },
                        {
                            "field_id": address_field_id,
                            "values": [{"value": order.address}],
                        },
                    ],
                    "_embedded": {
                        "contacts": [
                            {
                                "id": contact_id,
                            }
                        ]
                    },
                }
            ],
        )
        if not resp.ok:
            raise ClientError(resp.text)

        data = resp.json()
        return data

    def list_contacts(self):
        """https://www.amocrm.ru/developers/content/crm_platform/contacts-api"""
        url = urljoin(self._url, f"api/v4/contacts/")
        resp = self._http_client.get(
            url, headers={"Authorization": f"Bearer {self._access_token}"}
        )
        if not resp.ok:
            raise ClientError(resp.text)

        data = resp.json()
        return data

    def get_contact(self, id_: int):
        """https://www.amocrm.ru/developers/content/crm_platform/contacts-api"""
        url = urljoin(self._url, f"api/v4/contacts/{id_}")
        resp = self._http_client.get(
            url, headers={"Authorization": f"Bearer {self._access_token}"}
        )
        if not resp.ok:
            raise ClientError(resp.text)

        data = resp.json()
        return data

    def create_contact(self, name: str, phone: str) -> str:
        """https://www.amocrm.ru/developers/content/crm_platform/contacts-api"""
        url = urljoin(self._url, "api/v4/contacts")
        name_id = 430823
        email_id = 430825
        resp = self._http_client.post(
            url,
            headers={"Authorization": f"Bearer {self._access_token}"},
            json=[
                {
                    "first_name": name,
                    "created_by": self.ROBOT_ID,
                    "custom_fields_values": [
                        {
                            "field_id": name_id,
                            "values": [{"value": phone, "enum_id": 806581}],
                        }
                    ],
                }
            ],
        )
        if not resp.ok:
            raise ClientError(resp.text)

        data = resp.json()
        contact = data["_embedded"]["contacts"][0]
        return contact["id"]


client = Client(
    {
        "integration_id": settings.AMOCRM_INTEGRATION_ID,
        "secret_key": settings.AMOCRM_SECRET_KEY,
        "access_token": settings.AMOCRM_ACCESS_TOKEN,
        "auth_code": settings.AMOCRM_AUTH_CODE,
    }
)
