from __future__ import annotations

import http
import json
import logging
import secrets
from collections import defaultdict

import pendulum
import requests
from django import forms
from django.conf import settings
from django.contrib.auth import login
from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import F
from django.http import HttpResponse, JsonResponse
from django.views.generic.edit import BaseFormView

import shop.models
from shop import models
from shop.client import sms
from shop.models import CartProduct

logger = logging.getLogger(__name__)


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
    phone = "".join(l for l in phone if l.isdigit())
    if not phone:
        return ""

    if len(phone) == 11:
        phone = "7" + phone[1:]

    if len(phone) == 10:
        phone = "7" + phone

    return phone


class AuthRequestCode(BaseFormView):
    class Form(forms.Form):
        phone = forms.CharField(required=True)
        action = forms.CharField(required=True)

        def clean_phone(self):
            phone = normalize_phone(self.data["phone"])
            if len(phone) != 11:
                raise ValidationError("Телефон должен состоять из 11 цифр")

            return phone

    form_class = Form

    def form_valid(self, form):
        phone = form.cleaned_data["phone"]

        # todo: check why not works on sqlite
        if models.ConfirmCode.objects.filter(
            phone=phone,
            created_at__gte=pendulum.now().subtract(minutes=1),
        ).first():
            errors = {
                "phone": [
                    "Код был запрошен менее минуты назад. "
                    "Пожалуйста, повторите запрос спустя минуту."
                ]
            }
            return JsonResponse(
                data={"errors": errors},
                safe=False,
                status=http.HTTPStatus.BAD_REQUEST,
            )

        req_id = secrets.token_urlsafe(16)
        code = "".join(str(secrets.randbelow(9)) for _ in range(4))
        models.ConfirmCode.objects.create(
            id=req_id,
            code=code,
            phone=phone,
            action=form.cleaned_data["action"],
        )

        if settings.DEBUG:
            print(f"Verification code is: {code}")
        try:
            sms.client.send_sms(
                f"Eclair. Ваш код: {code}", phone, get_client_ip(self.request)
            )
        except sms.ClientError as err:
            logger.error("failed to send sms: %s", err)
            return JsonResponse(
                data={"errors": {"phone": ["Не удалось отправить смс"]}},
                safe=False,
                status=http.HTTPStatus.BAD_REQUEST,
            )

        return JsonResponse(data={"request_id": req_id}, safe=True)

    def form_invalid(self, form):
        errors = defaultdict(list)
        for field, errs in form.errors.items():
            for err in errs.data:
                errors[field].append(err.message)

        return JsonResponse(
            data={"errors": errors}, safe=False, status=http.HTTPStatus.BAD_REQUEST
        )


class ConfirmCode(BaseFormView):
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

        models.ConfirmCode.objects.filter(
            created_at__lte=pendulum.now().subtract(days=1)
        ).delete()

        try:
            confirmation = models.ConfirmCode.objects.get(
                id=req_id,
                phone=phone,
                code=code,
            )
        except models.ConfirmCode.DoesNotExist:
            return JsonResponse(
                data={"errors": {"code": ["Неверный код"]}},
                safe=False,
                status=http.HTTPStatus.BAD_REQUEST,
            )

        if confirmation.action == "login":
            user, _ = models.User.objects.get_or_create(
                phone=phone, defaults={"username": phone}
            )

            sid_old = self.request.session.session_key
            login(self.request, user)

            if sid_old:
                CartProduct.objects.filter(session_id=sid_old).update(
                    session_id=self.request.session.session_key
                )

        elif confirmation.action == "phone_change":
            self.request.user.phone = phone
            self.request.user.save()

        return JsonResponse(data={"success": True}, safe=False)

    def form_invalid(self, form):
        errors = defaultdict(list)
        for field, errs in form.errors.items():
            for err in errs.data:
                errors[field].append(err.message)

        return JsonResponse(
            data={"errors": errors}, safe=False, status=http.HTTPStatus.BAD_REQUEST
        )


class DeleteAddress(BaseFormView):
    class Form(forms.Form):
        address_id = forms.IntegerField(required=True)

    form_class = Form

    def form_valid(self, form):
        request: WSGIRequest = self.request
        if not request.user.is_authenticated:
            return JsonResponse(status=http.HTTPStatus.UNAUTHORIZED, data="")

        addr_id = form.cleaned_data["address_id"]
        addr = models.UserAddress.objects.get(id=addr_id, user_id=request.user.id)
        addr.delete()

        return JsonResponse(data={"success": True}, safe=False)

    def form_invalid(self, form):
        errors = defaultdict(list)
        for field, errs in form.errors.items():
            for err in errs.data:
                errors[field].append(err.message)

        return JsonResponse(
            data={"errors": errors}, safe=False, status=http.HTTPStatus.BAD_REQUEST
        )


def design_upload(request):
    image = request.FILES["file"]
    image_upload = models.CustomCakeDesignUploads(image=image, name=image.name)
    image_upload.save()
    return HttpResponse(content=image_upload.image, status=http.HTTPStatus.OK)


def get_client_ip(request: WSGIRequest):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[-1].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "")
    return ip
