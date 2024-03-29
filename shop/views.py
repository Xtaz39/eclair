from __future__ import annotations

from urllib.parse import urljoin

from django import forms
from django.conf import settings
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import BaseFormView, FormView

from . import models, validators
from .client import amocrm, recaptcha, yookassa
from .fields import MultiTextField, MultiTextInput


class CategoriesDataMixin:
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["categories"] = (
            models.Category.objects.exclude(product=None).order_by("position").all()
        )
        return data


class FooterDataMixin:
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        social = models.FooterSocial.objects.exclude(link=None).all()
        data["social"] = {s.media_type: s for s in social}

        data["phones"] = models.ContactNumber.objects.all()
        data["addresses"] = models.Address.objects.all()
        return data


class CartDataMixin:
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        req: WSGIRequest = self.request
        session = req.session.session_key
        if not session:
            return data

        items: list[models.CartProduct] = (
            models.CartProduct.objects.filter(session_id=session)
            .prefetch_related("product")
            .all()
        )
        data["cart_raw"] = items
        if not items:
            return data

        data["cart"] = {
            "products": [
                {"title": item.product_id, "amount": item.amount} for item in items
            ],
            "products_price": {
                item.product_id: float(item.product.price) for item in items
            },
            "products_amount": {item.product_id: item.amount for item in items},
            "qty_total": sum((p.amount for p in items)),
        }
        return data


class Index(CartDataMixin, FooterDataMixin, TemplateView):
    template_name = "shop/index/index.html"

    def _get_promoted_products(self) -> list[models.Product]:
        promoted_settings: models.PromotedProductsSettings = (
            models.PromotedProductsSettings.objects.first()
        )
        if not promoted_settings:
            return []

        limit = promoted_settings.limit
        if promoted_settings.mode == "auto":
            start, end = promoted_settings.get_period_interval()
            top_articles = (
                models.OrderProduct.objects.filter(
                    created_at__gte=start, created_at__lte=end
                )
                .values("article")
                .annotate(bought_times=Sum("amount"))
                .order_by("-bought_times")[:limit]
            )
            products = models.Product.objects.filter(
                article__in=(t["article"] for t in top_articles)
            )
            return products.all()[:limit]

        if promoted_settings.mode == "manual":
            pm = models.PromotedProductsManual.objects.select_related("product").all()[
                :limit
            ]
            return [p.product for p in pm]

        return []

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        categories = (
            models.Category.objects.prefetch_related(
                "product_set", "product_set__productimage_set"
            )
            .exclude(product=None)
            .order_by("position")
            .all()
        )
        data["categories"] = categories
        data["banners"] = models.Banner.objects.order_by("priority")
        data["promoted_products"] = self._get_promoted_products()

        return data


class Product(CartDataMixin, FooterDataMixin, CategoriesDataMixin, TemplateView):
    template_name = "shop/product.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        article = data["article"]
        product = get_object_or_404(
            models.Product.objects.prefetch_related("productimage_set"),
            article=article,
        )
        data["product"] = product
        data["recommendations"] = product.recommendations.all()
        return data


class Cabinet(CartDataMixin, FooterDataMixin, CategoriesDataMixin, FormView):
    class Form(forms.Form):
        first_name = forms.CharField(max_length=50, required=False)
        phone = forms.CharField(max_length=20, required=True)
        email = forms.EmailField(required=False)
        birthday = forms.DateField(required=False)
        addresses = MultiTextField(
            widget=MultiTextInput(),
            fields=tuple(
                forms.CharField(max_length=50, required=False) for _ in range(5)
            ),
            require_all_fields=False,
            required=False,
        )

    template_name = "shop/cabinet/cabinet.html"
    form_class = Form
    addresses_limit = 5

    def get_form_kwargs(self):
        kwargs = super(Cabinet, self).get_form_kwargs()
        kwargs["initial"]["first_name"] = self.request.user.first_name
        kwargs["initial"]["phone"] = self.request.user.phone
        kwargs["initial"]["email"] = self.request.user.email
        user_addrs = (
            models.UserAddress.objects.filter(user=self.request.user)
            .order_by("created_at")
            .all()[: self.addresses_limit]
        )
        kwargs["initial"]["addresses"] = [val for val in user_addrs]

        birthday = ""
        if self.request.user.birthday:
            birthday = self.request.user.birthday.strftime("%Y-%m-%d")
        kwargs["initial"]["birthday"] = birthday

        return kwargs

    def form_valid(self, form):
        user = self.request.user
        for f_name in form.changed_data:

            if f_name == "phone" or not hasattr(user, f_name):
                continue

            if f_name == "addresses":
                continue

            setattr(user, f_name, form.cleaned_data[f_name])

        user.save()

        return redirect("/cabinet")

    def get(self, request: WSGIRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(to="/")

        return super(Cabinet, self).get(request, *args, **kwargs)


class About(CartDataMixin, FooterDataMixin, CategoriesDataMixin, TemplateView):
    template_name = "shop/about.html"


class CakeOrder(CartDataMixin, FooterDataMixin, CategoriesDataMixin, TemplateView):
    template_name = "shop/cake-order.html"


class CakeStandard(CartDataMixin, FooterDataMixin, CategoriesDataMixin, FormView):
    template_name = "shop/cake-standard-constructor.html"

    class Form(forms.Form):
        design = forms.CharField(required=True)
        name = forms.CharField(required=True)
        phone = forms.CharField(required=True, validators=[validators.is_phone])
        email = forms.CharField(required=True)
        birthdate = forms.DateField(required=False)
        address = forms.CharField(required=True)
        delivery_date = forms.DateField(required=True)

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # self.fields["g-recaptcha-response"] = forms.CharField(required=True)

    form_class = Form

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["cake_designs"] = models.CakeStandard.objects.order_by("position").all()
        return data

    def form_valid(self, form):
        data = form.cleaned_data

        if not self.request.user.is_authenticated:
            captcha = data["g-recaptcha-response"]
            user_passed_captcha = recaptcha.client.check(captcha)
            if not user_passed_captcha:
                raise PermissionDenied

        design = models.CakeStandard.objects.get(pk=int(data["design"]))

        contact_id = amocrm.client.create_contact(
            name=data["name"],
            phone=data["phone"],
            email=data["email"],
            birthday=data["birthdate"],
        )

        content = f"Торт {design.title}\n"
        order_id = amocrm.client.order_cake(
            contact_id=contact_id,
            address=data["address"],
            content=content,
            delivery_date=data["delivery_date"],
        )

        return render(
            self.request,
            "shop/order_status.html",
            {
                "order_number": order_id,
                "message": "Ваш заказ принят. Наш менеджер свяжется с вами в ближайшее время.",
            },
        )


class CakeConstructor(CartDataMixin, FooterDataMixin, CategoriesDataMixin, FormView):
    class Form(forms.Form):
        cake_design = forms.CharField(required=False)
        cake_design_link = forms.CharField(required=False)
        cake_toppings = forms.CharField(required=True)
        # cake_postcards = forms.CharField(required=True)
        # cake_decors = forms.CharField(required=True)
        weight = forms.CharField(required=True)
        name = forms.CharField(required=True)
        phone = forms.CharField(required=True, validators=[validators.is_phone])
        birthdate = forms.DateField(required=False)
        address = forms.CharField(required=True)
        delivery_date = forms.DateField(required=True)
        delivery_time = forms.TimeField(required=True)
        comment = forms.CharField(required=False)

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields["g-recaptcha-response"] = forms.CharField(required=True)

        def clean(self):
            cleaned_data = super().clean()
            if not cleaned_data["cake_design"] and not cleaned_data["cake_design_link"]:
                raise forms.ValidationError("Нужно выбрать дизайн")

            return cleaned_data

    form_class = Form
    template_name = "shop/cake-constructor.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        designs_by_category = {}
        for cake in models.CakeDesign.objects.all():
            if cake.category in designs_by_category:
                designs_by_category[cake.category].append(cake)
            else:
                designs_by_category[cake.category] = [cake]

        data["cake_designs_by_category"] = designs_by_category
        data["cake_toppings"] = models.CakeTopping.objects.all()
        data["cake_decors"] = models.CakeDecor.objects.all()
        data["cake_postcards"] = models.CakePostcard.objects.all()
        return data

    def form_valid(self, form):
        data = form.cleaned_data

        if not self.request.user.is_authenticated:
            captcha = data["g-recaptcha-response"]
            user_passed_captcha = recaptcha.client.check(captcha)
            if not user_passed_captcha:
                raise PermissionDenied

        if not data["cake_design"]:
            uploaded_img = models.CustomCakeDesignUploads.objects.order_by(
                "created_at"
            ).get(name=data["cake_design_link"])
            design_title = urljoin(settings.SITE_ADDR, uploaded_img.image.url)
        else:
            design = models.CakeDesign.objects.get(pk=int(data["cake_design"])).title
            design_title = design.title

        toppings = models.CakeTopping.objects.filter(
            pk__in=[int(id_) for id_ in data["cake_toppings"].split(",")]
        )
        # decors = models.CakeDecor.objects.filter(
        #     pk__in=[int(id_) for id_ in data["cake_decors"].split(",")]
        # )
        # postcards = models.CakePostcard.objects.filter(
        #     pk__in=[int(id_) for id_ in data["cake_postcards"].split(",")]
        # )

        contact_id = amocrm.client.create_contact(
            name=data["name"],
            phone=data["phone"],
            birthday=data["birthdate"],
        )

        toppings_names = ", ".join(topping.title for topping in toppings)
        # decor_names = ", ".join(decor.title for decor in decors)
        # postcard_names = ", ".join(postcard.title for postcard in postcards)

        content = (
            f"Торт {design_title}\n"
            f"Начинки: {toppings_names}.\n"
            # f"Открытки: {postcard_names}.\n"
            # f"Декор: {decor_names}."
        )
        order_id = amocrm.client.order_custom_cake(
            contact_id,
            content=content,
            delivery_date=data["delivery_date"],
            delivery_time=data["delivery_time"],
            address=data["address"],
            weight=f"{data['weight']} кг",
            comment=data["comment"],
        )

        return render(
            self.request,
            "shop/order_status.html",
            {
                "order_number": order_id,
                "message": "Ваш заказ принят. Наш менеджер свяжется с вами в ближайшее время.",
            },
        )


class Contacts(CartDataMixin, FooterDataMixin, CategoriesDataMixin, TemplateView):
    template_name = "shop/contacts.html"


class News(CartDataMixin, FooterDataMixin, CategoriesDataMixin, TemplateView):
    template_name = "shop/news.html"


class NewsItem(CartDataMixin, FooterDataMixin, CategoriesDataMixin, TemplateView):
    template_name = "shop/news-item.html"


class Cart(CartDataMixin, FooterDataMixin, CategoriesDataMixin, TemplateView):
    template_name = "shop/cart.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        req: WSGIRequest = self.request
        session = req.session.session_key
        if not session:
            return data

        items = (
            models.CartProduct.objects.filter(session_id=session, amount__gt=0)
            .prefetch_related(
                "product__productimage_set",
                "product",
                "product__category",
                "product__recommendations",
            )
            .all()
        )
        if not items:
            return data

        product_in_cart = [item.product_id for item in items]
        recommendations = (
            models.Product.recommendations.through.objects.filter(
                from_product__in=product_in_cart
            )
            .exclude(to_product__in=product_in_cart)
            .all()
        )

        product_recommendations = []
        recommended_products_ids = set()
        for recommendation in recommendations:
            if recommendation.to_product in recommended_products_ids:
                continue

            recommended_products_ids.add(recommendation.to_product)
            product_recommendations.append(recommendation.to_product)

        data["cart_items"] = items
        data["product_recommendations"] = product_recommendations
        return data


class Checkout(CartDataMixin, FooterDataMixin, CategoriesDataMixin, FormView):
    class Form(forms.Form):
        name = forms.CharField(required=True)
        phone = forms.CharField(required=True, validators=[validators.is_phone])
        street = forms.CharField(required=True)
        house = forms.CharField(required=True)
        room = forms.CharField(required=False)
        entrance = forms.CharField(required=False)
        floor = forms.CharField(required=False)
        doorphone = forms.CharField(required=False)
        comment = forms.Textarea()
        pay_method = forms.CharField(required=True)

    form_class = Form
    template_name = "shop/checkout.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            kwargs["initial"]["name"] = self.request.user.first_name
            kwargs["initial"]["phone"] = self.request.user.phone

            address = (
                models.UserAddress.objects.filter(user=self.request.user)
                .order_by("created_at")
                .reverse()
                .first()
            )
            if address:
                kwargs["initial"]["street"] = address.street
                kwargs["initial"]["house"] = address.house
                kwargs["initial"]["room"] = address.room
                kwargs["initial"]["entrance"] = address.entrance
                kwargs["initial"]["floor"] = address.floor
                kwargs["initial"]["doorphone"] = address.doorphone

        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        req: WSGIRequest = self.request
        session = req.session.session_key
        if not session:
            return data

        items = (
            models.CartProduct.objects.filter(session_id=session)
            .prefetch_related("product", "product__category")
            .all()
        )

        data["cart_items"] = items
        data["cart_total_amount"] = sum(
            item.amount * item.product.price for item in items
        )
        if self.request.user.is_authenticated:
            data["user_addresses"] = (
                models.UserAddress.objects.filter(user=self.request.user)
                .order_by("created_at")
                .reverse()
                .all()[:5]
            )

        return data

    @transaction.atomic
    def form_valid(self, form):
        request: WSGIRequest = self.request
        if not self.request.session.session_key:
            raise Http404()

        customer = form.cleaned_data
        order_items = (
            models.CartProduct.objects.filter(session_id=request.session.session_key)
            .prefetch_related("product")
            .all()
        )

        addr_parts = [
            customer["street"],
            customer["house"],
            customer["room"],
            customer["entrance"],
            customer["floor"],
            customer["doorphone"],
        ]
        address = ",".join(part for part in addr_parts if part)

        order = models.Order.objects.create(
            order_number=models.Order.generate_order_number(),
            customer_name=customer["name"],
            phone=customer["phone"],
            address=address,
            payment_type=customer["pay_method"],
            session_id=request.session.session_key,
        )
        order_products = [
            models.OrderProduct(
                order_id=order.pk,
                article=item.product.article,
                title=item.product.title,
                price=item.product.price,
                amount=item.amount,
            )
            for item in order_items
        ]
        models.OrderProduct.objects.bulk_create(order_products)

        # clear cart
        models.CartProduct.objects.filter(
            session_id=request.session.session_key
        ).delete()

        # remember address
        address_already_exists = models.UserAddress.objects.filter(
            street=customer["street"],
            house=customer["house"],
            room=customer["room"],
            entrance=customer["entrance"],
            floor=customer["floor"],
            doorphone=customer["doorphone"],
        ).exists()
        if not address_already_exists:
            models.UserAddress.objects.create(
                user=request.user,
                street=customer["street"],
                house=customer["house"],
                room=customer["room"],
                entrance=customer["entrance"],
                floor=customer["floor"],
                doorphone=customer["doorphone"],
            )

        if customer["pay_method"] == "card":
            redirect_url = reverse(
                "shop:online-payment",
                kwargs={
                    "order_number": order.order_number,
                },
            )
        else:
            redirect_url = reverse(
                "shop:order-success",
                kwargs={
                    "order_number": order.order_number,
                },
            )

        return redirect(to=redirect_url)


class OnlinePayment(CartDataMixin, FooterDataMixin, CategoriesDataMixin, TemplateView):
    template_name = "shop/online_payment.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        if not self.request.session.session_key or not kwargs["order_number"]:
            raise Http404()

        order_number = kwargs["order_number"]
        try:
            order = models.Order.objects.get(
                session_id=self.request.session.session_key,
                order_number=order_number,
            )
        except models.Order.DoesNotExist:
            raise Http404()

        products = models.OrderProduct.objects.filter(order=order).all()
        order_total = sum(item.amount * item.price for item in products)

        confirmation_token = yookassa.client.generate_payment_yoo(
            phone=order.phone,
            email=self.request.user.email,
            order_number=order.order_number,
            total_amount=order_total,
            products=products,
        )
        return_url = reverse(
            "shop:order-success",
            kwargs={
                "order_number": order.order_number,
            },
        )
        data["confirmation_token"] = confirmation_token
        data["return_url"] = urljoin(settings.SITE_ADDR, return_url)
        data["order_number"] = order_number
        data["order_total"] = int(order_total)

        return data


class OrderSuccess(CartDataMixin, FooterDataMixin, CategoriesDataMixin, TemplateView):
    template_name = "shop/order_status.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if not self.request.session.session_key or not kwargs["order_number"]:
            raise Http404()

        order_number = kwargs["order_number"]
        try:
            order = models.Order.objects.get(
                session_id=self.request.session.session_key,
                order_number=order_number,
            )
        except models.Order.DoesNotExist:
            raise Http404()

        msg = "Ваш заказ успешно создан"
        if order.payment_type == "card":
            # if sberbank.client.check_order_payed(order_number):
            #     msg = "Ваш заказ успешно оплачен"
            # else:
            #     msg = "Не удалось оплатить заказ"
            msg = "Ваш заказ успешно оплачен"

        data["order_number"] = kwargs["order_number"]
        data["message"] = msg
        return data


class PaymentFailed(CartDataMixin, FooterDataMixin, CategoriesDataMixin, TemplateView):
    def get(self, request: WSGIRequest, *args, **kwargs):
        if "order_number" not in kwargs:
            raise Http404()

        return render(
            request,
            "shop/order_status.html",
            context={
                "order_number": kwargs["order_number"],
                "message": "Не удалось оплатить заказ",
            },
        )


class RefreshClientToken(BaseFormView):
    def get(self, request, *args, **kwargs):
        token = kwargs["token"]
        amocrm.client._auth_code = token
        access_token, refresh_token = amocrm.client._request_access_token()
        amocrm.client._tokens_write(access_token, refresh_token)
        return HttpResponse("Done 👍")


class Review(CartDataMixin, FooterDataMixin, CategoriesDataMixin, TemplateView):
    template_name = "shop/review.html"


class Vacancies(CartDataMixin, FooterDataMixin, CategoriesDataMixin, TemplateView):
    template_name = "shop/vacancies.html"


class NotFound(CartDataMixin, FooterDataMixin, CategoriesDataMixin, TemplateView):
    template_name = "shop/error_code.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        msgs = {
            400: "Неправильный запрос",
            403: "Доступ запрещен",
            404: "Страница не найдена",
            500: "Что-то пошло не так. Информация передана разработчикам",
        }
        msg = msgs.get(kwargs["code"], "Что-то пошло не так")

        kwargs["error_message"] = msg
        kwargs["error_code"] = kwargs.pop("code")
        return kwargs


def error_400(request, exception=None):
    return NotFound.as_view()(request, code=400)


def error_403(request, exception=None):
    return NotFound.as_view()(request, code=403)


def error_404(request, exception=None):
    return NotFound.as_view()(request, code=404)


def error_500(request, exception=None):
    return NotFound.as_view()(request, code=500)


def logout_user(request):
    logout(request)

    ref = request.META.get("HTTP_REFERER", "")
    if not ref:
        return redirect("/")

    return redirect(ref)
