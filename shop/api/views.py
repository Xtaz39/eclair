from django.core.handlers.wsgi import WSGIRequest
from django.db.models import F
from django.http import HttpResponse
from django.views.generic.edit import BaseFormView

from shop.models import CartProduct


class Cart(BaseFormView):
    def get(self, request: WSGIRequest, *args, **kwargs):
        if not request.session.session_key:
            request.session.create()

        cart_product, is_new = CartProduct.objects.get_or_create(
            product_id="donat-chocolate", session_id=request.session.session_key
        )
        if not is_new:
            cart_product.amount = F("amount") + 1
            cart_product.save()

        return HttpResponse("Ok")

    def post(self, request, *args, **kwargs):
        return HttpResponse("Ok Post")

    def delete(self, request: WSGIRequest, *args, **kwargs):
        return HttpResponse("Ok Delete")
