from __future__ import annotations

import http
import json
import secrets
import uuid

from django.contrib.auth import login
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import F
from django.http import HttpResponse, JsonResponse
from django.views.generic.edit import BaseFormView

from shop import models
from shop.models import CartProduct


class Cart(BaseFormView):
    def get(self, request: WSGIRequest, *args, **kwargs):
        if not request.session.session_key:
            return JsonResponse(data=[], safe=False)

        cart_product = CartProduct.objects.filter(
            session_id=request.session.session_key
        ).all()

        products = [{"title": p.product_id, "amount": p.amount} for p in cart_product]
        return JsonResponse(data=products, safe=False)

    def put(self, request: WSGIRequest, *args, **kwargs):
        data = json.loads(self.request.body)
        article = data["article"]
        amount = data["amount"]

        if not request.session.session_key:
            request.session.create()

        cart_product, is_new = CartProduct.objects.get_or_create(
            product_id=article, session_id=request.session.session_key
        )
        if not is_new:
            if cart_product.amount + amount <= 0:
                cart_product.delete()
            else:
                # Todo: check that new amount won't exceed stock or some limit
                cart_product.amount = F("amount") + amount
                cart_product.save()

        return HttpResponse(status=http.HTTPStatus.CREATED)


class AuthRequestCode(BaseFormView):
    def post(self, request, *args, **kwargs):
        phone = request.POST.get("phone")
        # todo: validate

        req_id = secrets.token_urlsafe(16)
        code = "".join(str(secrets.randbelow(9)) for _ in range(4))
        models.AuthCode.objects.create(
            id=req_id,
            code=code,
            phone=phone,
        )
        data = {"request_id": req_id}

        print(f"Login code is: {code}")
        # todo: send sms code
        return JsonResponse(data=data, safe=True)


class AuthLogin(BaseFormView):
    def post(self, request: WSGIRequest, *args, **kwargs):
        phone = request.POST.get("phone")
        code = request.POST.get("code")
        req_id = request.POST.get("request_id")
        # todo: validate

        # todo: clear old records here?

        deleted, _ = models.AuthCode.objects.filter(
            id=req_id,
            phone=phone,
            code=code,
        ).delete()

        if not deleted:
            # todo: return err
            return JsonResponse(
                data={"success": False}, safe=False, status=http.HTTPStatus.BAD_REQUEST
            )

        user, _ = models.User.objects.get_or_create(phone=phone)
        login(request, user)
        return JsonResponse(data={"success": True}, safe=False)
