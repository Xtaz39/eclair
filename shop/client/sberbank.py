import requests
from urllib.parse import urljoin

from eclair import settings


class ClientError(Exception):
    pass


class Client:
    def __init__(self, url: str, username: str, password: str):
        self._base_url = url
        self._username = username
        self._password = password
        self._http_client = requests.Session()

    def generate_payment(self, order: str, amount: int) -> str:
        """
        https://securepayments.sberbank.ru/wiki/doku.php/integration:api:rest:requests:register
        """
        resp = self._http_client.post(
            urljoin(self._base_url, "register.do"),
            data={
                "userName": self._username,
                "password": self._password,
                "orderNumber": order,
                # умножаем на 100 так как сумма отправляется в копейках
                "amount": amount * 100,
                "returnUrl": f"http://127.0.0.1:8000/order/success/{order}",
                "failUrl": f"http://127.0.0.1:8000/order/fail/{order}",
            },
            headers={"Content-type": "application/x-www-form-urlencoded"},
        )
        if not resp.ok:
            raise ClientError(f"Error {resp.status_code}: {resp.text}")

        data = resp.json()
        if "errorCode" in data:
            raise ClientError(f"Error {data['errorCode']}: {data['errorMessage']}")

        return data["formUrl"]

    def check_order_payed(self, order: str) -> bool:
        """
        https://securepayments.sberbank.ru/wiki/doku.php/integration:api:rest:requests:getorderstatusextended

        :orderStatus Целое число
         По значению этого параметра определяется состояние заказа в платёжной системе.
         Отсутствует, если заказ не был найден. Ниже представлен список возможных значений:
            0 - заказ зарегистрирован, но не оплачен;
            1 - предавторизованная сумма удержана (для двухстадийных платежей);
            2 - проведена полная авторизация суммы заказа;
            3 - авторизация отменена;
            4 - по транзакции была проведена операция возврата;
            5 - инициирована авторизация через сервер контроля доступа банка-эмитента;
            6 - авторизация отклонена.
        """
        resp = self._http_client.post(
            urljoin(self._base_url, "getOrderStatusExtended.do"),
            data={
                "userName": self._username,
                "password": self._password,
                "orderNumber": order,
            },
            headers={"Content-type": "application/x-www-form-urlencoded"},
        )
        if not resp.ok:
            raise ClientError(f"Error {resp.status_code}: {resp.text}")

        data = resp.json()
        if "errorCode" in data and data["errorCode"] != "0":
            raise ClientError(f"Error {data['errorCode']}: {data['errorMessage']}")

        payment_held, payed = 1, 2
        return data["orderStatus"] in (payment_held, payed)


client = Client(
    settings.SBERBANK_URL, settings.SBERBANK_USER, settings.SBERBANK_PASSWORD
)
