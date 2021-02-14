import os
from urllib.parse import urljoin

import requests

integration_id = os.environ.get("AMOCRM_INTEGRATION_ID")
secret_key = os.environ.get("AMOCRM_SECRET_KEY")
auth_code = os.environ.get("AMOCRM_AUTH_CODE")
access_token = os.environ.get("AMOCRM_ACCESS_TOKEN")
refresh_token = os.environ.get("AMOCRM_REFRESH_TOKEN")


class PaymentType:
    CASH = 34113529
    CARD = 34113523


class Client:
    SITE_PIPELINE_ID = 3428449
    ROBOT_ID = 0

    def __init__(self):
        self.url = "https://dennabiullin.amocrm.ru"
        self.access_token = access_token
        self.refresh_token = refresh_token

    def _get_access_token(self):
        """https://www.amocrm.ru/developers/content/oauth/step-by-step#get_access_token"""
        url = urljoin(self.url, "/oauth2/access_token")
        resp = requests.post(
            url,
            data={
                "client_id": integration_id,
                "client_secret": secret_key,
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": "https://dmssk.github.io/",
            },
        )
        if not resp.ok:
            return

        data = resp.json()
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        return

    def _refresh_token(self):
        url = urljoin(self.url, "/oauth2/access_token")
        resp = requests.post(
            url,
            data={
                "client_id": integration_id,
                "client_secret": secret_key,
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "redirect_uri": "https://dmssk.github.io/",
            },
        )
        if not resp.ok:
            return

        data = resp.json()
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        return

    def get_leads(self):
        """https://www.amocrm.ru/developers/content/crm_platform/leads-api"""
        url = urljoin(self.url, "api/v4/leads")
        resp = requests.get(
            url, headers={"Authorization": f"Bearer {self.access_token}"}
        )
        if not resp.ok:
            return

        data = resp.json()
        return data

    def get_lead(self, id: int):
        """https://www.amocrm.ru/developers/content/crm_platform/leads-api"""
        url = urljoin(self.url, f"api/v4/leads/{id}")
        resp = requests.get(
            url, headers={"Authorization": f"Bearer {self.access_token}"}
        )
        if not resp.ok:
            return

        data = resp.json()
        return data

    def create_lead(self):
        """https://www.amocrm.ru/developers/content/crm_platform/leads-api"""
        url = urljoin(self.url, "api/v4/leads")
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {self.access_token}"},
            json=[
                {
                    "name": "тестовая сделка (наличные)",
                    "price": 999,
                    "pipeline_id": self.SITE_PIPELINE_ID,
                    "created_by": self.ROBOT_ID,
                    "status_id": PaymentType.CASH,
                    "custom_fields_values": [
                        {"field_id": 472641, "values": [{"value": "value1"}]}
                    ],
                    "_embedded": {
                        # https://www.amocrm.ru/developers/content/crm_platform/custom-fields#cf-fill-examples
                        "contacts": [
                            {
                                "id": 40154837,
                            }
                        ]
                    },
                }
            ],
        )
        if not resp.ok:
            return

        data = resp.json()
        return data

    def list_contacts(self, id_: int):
        """https://www.amocrm.ru/developers/content/crm_platform/contacts-api"""
        url = urljoin(self.url, f"api/v4/contacts/{id_}")
        resp = requests.get(
            url, headers={"Authorization": f"Bearer {self.access_token}"}
        )
        if not resp.ok:
            return

        data = resp.json()
        return data

    def get_contact(self, id: int):
        """https://www.amocrm.ru/developers/content/crm_platform/contacts-api"""
        url = urljoin(self.url, f"api/v4/contacts/{id}")
        resp = requests.get(
            url, headers={"Authorization": f"Bearer {self.access_token}"}
        )
        if not resp.ok:
            return

        data = resp.json()
        return data

    def create_contact(self):
        """https://www.amocrm.ru/developers/content/crm_platform/contacts-api"""
        url = urljoin(self.url, "api/v4/contacts")
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {self.access_token}"},
            json=[
                {
                    "first_name": "Test",
                    "last_name": "Testerov",
                    "created_by": self.ROBOT_ID,
                    "custom_fields_values": [
                        {
                            "field_id": 430823,
                            "values": [{"value": "+79999999999", "enum_id": 806581}],
                        },
                        {
                            "field_id": 430825,
                            "values": [{"value": "auto@test.test", "enum_id": 806593}],
                        },
                    ],
                }
            ],
        )
        if not resp.ok:
            return

        data = resp.json()
        contact = data["_embedded"]["contacts"][0]
        return contact["id"]


client = Client()
account = client.create_lead()
print(account)

# {'id': 23929449, 'name': 'тест ручной', 'price': 999, 'responsible_user_id': 3327907, 'group_id': 0, 'status_id': 34113523, 'pipeline_id': 3428449, 'loss_reason_id': None, 'created_by': 3327907, 'updated_by': 3327907, 'created_at': 1613312594, 'updated_at': 1613312594, 'closed_at': None, 'closest_task_at': None, 'is_deleted': False, 'custom_fields_values': [{'field_id': 472641, 'field_name': 'Что желаете заказать', 'field_code': None, 'field_type': 'text', 'values': [{'value': 'мой заказ'}]}], 'score': None, 'account_id': 25194517, '_links': {'self': {'href': 'https://dennabiullin.amocrm.ru/api/v4/leads/23929449'}}, '_embedded': {'tags': [], 'companies': []}}

# {'id': 40154837, 'name': 'Покупатель', 'first_name': '', 'last_name': '', 'responsible_user_id': 3327907, 'group_id': 0, 'created_by': 3327907, 'updated_by': 3327907, 'created_at': 1613312594, 'updated_at': 1613312594, 'closest_task_at': None, 'custom_fields_values': [{'field_id': 430823, 'field_name': 'Телефон', 'field_code': 'PHONE', 'field_type': 'multitext', 'values': [{'value': '+79999999999', 'enum_id': 806581, 'enum_code': 'WORK'}]}, {'field_id': 430825, 'field_name': 'Email', 'field_code': 'EMAIL', 'field_type': 'multitext', 'values': [{'value': 'test@testov.test', 'enum_id': 806593, 'enum_code': 'WORK'}]}], 'account_id': 25194517, '_links': {'self': {'href': 'https://dennabiullin.amocrm.ru/api/v4/contacts/40154837'}}, '_embedded': {'tags': [], 'companies': []}}
