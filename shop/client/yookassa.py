import var_dump as var_dump
import requests

from yookassa import Settings
from yookassa import Configuration
from yookassa import Payment
from yookassa.domain.models.currency import Currency
from yookassa.domain.models.receipt import Receipt
from yookassa.domain.models.receipt_item import ReceiptItem
from yookassa.domain.common.confirmation_type import ConfirmationType
from yookassa.domain.request.payment_request_builder import PaymentRequestBuilder

from django.contrib.auth.models import AbstractUser
from django.db import models

from urllib.parse import urljoin

from eclair import settings
from __future__ import annotations
from django.http import JsonResponse
from django.core.handlers.wsgi import WSGIRequest


class Client:
    def __init__(self, url: str, shopid: str, secretkey: str, redirect_addr: str):
        self._base_url = url
        self._shopid = shopid
        self._secretkey = secretkey
        self._http_client = requests.Session()
        self._redirect_addr = redirect_addr

        def get_client_ip(request: WSGIRequest):
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            return ip

        def get_order_product(self):
            cart_product = self.request.OrderProduct.objects.filter(
                session_id=self.request.session.session_key
            ).all()
            products = [{"description": p.title, "quantity": p.amount, "amount": {"value": p.price,
                                                                                  "currency": Currency.RUB},
                         "vat_code": 2} for p in cart_product]
            return JsonResponse(data=products, safe=False)

        def generate_payment_yoo(self, order: str, amount: int) -> str:
            Configuration.account_id = shopid
            Configuration.secret_key = secretkey

            receipt = Receipt()
            receipt.customer = {"phone": self.request.user.phone, "email": self.request.user.email}
            receipt.tax_system_code = 2
            receipt.items = [
                ReceiptItem(get_order_product(self))
            ]

            builder = PaymentRequestBuilder()
            builder.set_amount({"value": amount, "currency": Currency.RUB}) \
                .set_confirmation(
                {"type": ConfirmationType.REDIRECT, "return_url": redirect_addr}) \
                .set_capture(False) \
                .set_description("Заказ №" + order) \
                .set_metadata({"orderNumber": order}) \
                .set_receipt(receipt)

            request = builder.build()
            request.client_ip = get_client_ip(self.request)
            print(request.confirmation)
            res = Payment.create(request)
            var_dump.var_dump(res)

client = Client(
    settings.SBERBANK_URL,
    settings.SBERBANK_USER,
    settings.SBERBANK_PASSWORD,
    settings.SITE_ADDR,
)