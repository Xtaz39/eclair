from __future__ import annotations

import http
import json
import secrets
from collections import defaultdict

import pendulum
from django import forms
from django.contrib.auth import login
from django.core.exceptions import ValidationError
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


def normalize_phone(phone: str) -> str:
    had_plus = phone.startswith("+")
    phone = "".join(l for l in phone if l.isdigit())
    if not phone:
        return ""

    if had_plus:
        phone = str(int(phone[0]) + 1) + phone[1:]

    return phone


class AuthRequestCode(BaseFormView):
    class Form(forms.Form):
        phone = forms.CharField(required=True)

        def clean_phone(self):
            phone = normalize_phone(self.data["phone"])
            if len(phone) != 11:
                raise ValidationError("Телефон должен состоять из 11 цифр")

            return phone

    form_class = Form

    def form_valid(self, form):
        phone = form.cleaned_data["phone"]

        # todo: check why not works on sqlite
        if models.AuthCode.objects.filter(
            phone=phone,
            created_at__gte=pendulum.now().subtract(minutes=1),
        ).first():
            errors = {
                "phone": (
                    "Код был запрошен менее минуты назад. "
                    "Пожалуйста, повторите запрос спустя время"
                )
            }
            return JsonResponse(
                data={"errors": errors},
                safe=False,
                status=http.HTTPStatus.BAD_REQUEST,
            )

        req_id = secrets.token_urlsafe(16)
        code = "".join(str(secrets.randbelow(9)) for _ in range(4))
        models.AuthCode.objects.create(
            id=req_id,
            code=code,
            phone=phone,
        )

        print(f"Login code is: {code}")
        # todo: send sms code
        return JsonResponse(data={"request_id": req_id}, safe=True)

    def form_invalid(self, form):
        errors = defaultdict(list)
        for field, errs in form.errors.items():
            for err in errs.data:
                errors[field].append(err.message)

        return JsonResponse(
            data={"errors": errors}, safe=False, status=http.HTTPStatus.BAD_REQUEST
        )


class AuthLogin(BaseFormView):
    class Form(forms.Form):
        phone = forms.CharField(required=True)
        code = forms.CharField(required=True)
        request_id = forms.CharField(required=True)

        def clean_phone(self):
            phone = normalize_phone(self.data["phone"])
            if len(phone) != 11:
                raise ValidationError("Телефон должен состоять из 11 цифр")

            return phone

    form_class = Form

    def form_valid(self, form):
        phone = form.cleaned_data["phone"]
        code = form.cleaned_data["code"]
        req_id = form.cleaned_data["request_id"]

        # todo: clear old records here?

        deleted, _ = models.AuthCode.objects.filter(
            id=req_id,
            phone=phone,
            code=code,
        ).delete()

        if not deleted:
            return JsonResponse(
                data={"errors": {"code": ["Неверный код"]}},
                safe=False,
                status=http.HTTPStatus.BAD_REQUEST,
            )

        user, _ = models.User.objects.get_or_create(
            phone=phone, defaults={"username": phone}
        )
        login(self.request, user)
        return JsonResponse(data={"success": True}, safe=False)

    def form_invalid(self, form):
        errors = defaultdict(list)
        for field, errs in form.errors.items():
            for err in errs.data:
                errors[field].append(err.message)

        return JsonResponse(
            data={"errors": errors}, safe=False, status=http.HTTPStatus.BAD_REQUEST
        )
