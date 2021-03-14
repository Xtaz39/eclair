from __future__ import annotations

from django import forms
from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import BaseFormView, FormView

from . import models, validators
from .client import amocrm, sberbank


class CategoriesDataMixin:
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["categories"] = models.Category.objects.exclude(product=None).all()
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


class Cabinet(CartDataMixin, FooterDataMixin, CategoriesDataMixin, TemplateView):
    template_name = "shop/cabinet.html"


class About(CartDataMixin, FooterDataMixin, CategoriesDataMixin, TemplateView):
    template_name = "shop/about.html"


class CakeOrder(CartDataMixin, FooterDataMixin, CategoriesDataMixin, TemplateView):
    template_name = "shop/cake-order.html"


class CakeConstructor(CartDataMixin, FooterDataMixin, CategoriesDataMixin, FormView):
    class Form(forms.Form):
        cake_design = forms.CharField(required=True)
        cake_toppings = forms.CharField(required=True)
        cake_postcards = forms.CharField(required=True)
        cake_decors = forms.CharField(required=True)
        weight = forms.CharField(required=True)
        name = forms.CharField(required=True)
        phone = forms.CharField(required=True, validators=[validators.is_phone])
        email = forms.CharField(required=True)
        birthdate = forms.DateField(required=False)
        address = forms.CharField(required=True)
        delivery_date = forms.DateField(required=True)
        delivery_time = forms.TimeField(required=True)
        comment = forms.CharField(required=False)

    form_class = Form
    template_name = "shop/cake-constructor.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["cake_designs"] = models.CakeDesign.objects.all()
        data["cake_toppings"] = models.CakeTopping.objects.all()
        data["cake_decors"] = models.CakeDecor.objects.all()
        data["cake_postcards"] = models.CakePostcard.objects.all()
        return data

    def form_valid(self, form):
        data = form.cleaned_data

        design = models.CakeDesign.objects.get(pk=int(data["cake_design"]))
        toppings = models.CakeTopping.objects.filter(
            pk__in=[int(id_) for id_ in data["cake_toppings"].split(",")]
        )
        decors = models.CakeDecor.objects.filter(
            pk__in=[int(id_) for id_ in data["cake_decors"].split(",")]
        )
        postcards = models.CakePostcard.objects.filter(
            pk__in=[int(id_) for id_ in data["cake_postcards"].split(",")]
        )

        contact_id = amocrm.client.create_contact(
            name=data["name"],
            phone=data["phone"],
            email=data["email"],
            birthday=data["birthdate"],
        )

        toppings_names = ", ".join(topping.title for topping in toppings)
        decor_names = ", ".join(decor.title for decor in decors)
        postcard_names = ", ".join(postcard.title for postcard in postcards)

        content = (
            f"Торт {design.title}\n"
            f"Начинки: {toppings_names}.\n"
            f"Открытки: {postcard_names}.\n"
            f"Декор: {decor_names}."
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
        address = forms.CharField(required=True)
        pay_method = forms.CharField(required=True)

    form_class = Form
    template_name = "shop/checkout.html"

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

        total_amount = sum(item.amount * item.product.price for item in order_items)
        order = models.Order.objects.create(
            order_number=models.Order.generate_order_number(),
            customer_name=customer["name"],
            phone=customer["phone"],
            address=customer["address"],
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

        client_card_id = amocrm.client.create_contact(
            customer["name"], customer["phone"]
        )

        order_content = "\n".join(
            (
                f"{item.product.title} x {item.amount} по {item.product.price}"
                for item in order_items
            )
        )

        payment_type = amocrm.PaymentType.CASH.value
        if customer["pay_method"] == "card":
            payment_type = amocrm.PaymentType.CARD.value

        amocrm.client.create_order(
            client_card_id,
            amocrm.Order(
                order_id=order.order_number,
                total_amount=int(total_amount),
                payment_type=payment_type,
                content=order_content,
                address=customer["address"],
            ),
        )

        if customer["pay_method"] == "card":
            payment_url = sberbank.client.generate_payment(
                order.order_number, int(total_amount)
            )
            return redirect(to=payment_url)

        return redirect(
            to=reverse(
                "shop:order-success",
                kwargs={
                    "order_number": order.order_number,
                },
            ),
        )


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
            if sberbank.client.check_order_payed(order_number):
                msg = "Ваш заказ успешно оплачен"
            else:
                msg = "Не удалось оплатить заказ"

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
        amocrm.client._obtain_access_token_external()
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
