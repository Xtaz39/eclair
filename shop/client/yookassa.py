from typing import List

from yookassa import Configuration
from yookassa import Payment
from yookassa.domain.common.confirmation_type import ConfirmationType
from yookassa.domain.models.currency import Currency
from yookassa.domain.models.receipt import Receipt
from yookassa.domain.models.receipt_item import ReceiptItem
from yookassa.domain.request.payment_request_builder import PaymentRequestBuilder

from eclair import settings
from shop import models


class Client:
    def __init__(self, shop_id: str, secret_key: str, tax_system_code: 2):
        Configuration.configure(shop_id, secret_key)
        self._tax_system_code = tax_system_code

    def generate_payment_yoo(
        self,
        phone: str,
        email: str,
        order_number: str,
        total_amount: int,
        products: List[models.OrderProduct],
    ) -> str:
        receipt = Receipt()
        receipt.tax_system_code = self._tax_system_code
        receipt.customer.phone = phone
        if email:
            receipt.customer.email = email

        receipt.items = [
            ReceiptItem(
                description=product.title,
                quantity=product.amount,
                amount={
                    "value": product.price,
                    "currency": Currency.RUB,
                },
                vat_code=2,  # self._tax_system_code ???
            )
            for product in products
        ]

        builder = PaymentRequestBuilder()
        builder.set_amount(
            {"value": total_amount, "currency": Currency.RUB}
        ).set_confirmation({"type": ConfirmationType.EMBEDDED}).set_description(
            "Заказ №" + order_number
        ).set_metadata(
            {"orderNumber": order_number}
        ).set_receipt(
            receipt
        )

        # https://yookassa.ru/developers/payments/payment-process#capture-and-cancel
        builder.set_capture(True)

        request = builder.build()

        response = Payment.create(request, idempotency_key=order_number)
        return response.confirmation.confirmation_token


client = Client(
    settings.YOOKASSA_SHOP_ID,
    settings.YOOKASSA_SECRET_KEY,
    settings.YOOKASSA_TAX_SYSTEM_CODE,
)
