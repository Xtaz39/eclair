import http

from django.core.handlers.wsgi import WSGIRequest
from django import forms
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.views.generic.edit import BaseFormView

from . import models


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
        if not (session := req.session.session_key):
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
            return models.Product.objects.all()[:limit]

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


class Checkout(CartDataMixin, FooterDataMixin, CategoriesDataMixin, TemplateView):
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


class OrderCreate(BaseFormView):
    class Form(forms.Form):
        name = forms.CharField()
        phone = forms.CharField()
        address = forms.CharField()
        pay_method = forms.CharField()

    form_class = Form

    def post(self, request: WSGIRequest, *args, **kwargs):
        if not request.session.session_key:
            raise Http404()

        form = self.get_form()
        if not form.is_valid():
            return HttpResponse(str(form.errors), status=http.HTTPStatus.BAD_REQUEST)

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

        return HttpResponse(
            f"Done! Your order for {total_amount} руб. is {order.order_number}"
        )


class Review(CartDataMixin, FooterDataMixin, CategoriesDataMixin, TemplateView):
    template_name = "shop/review.html"


class Vacancies(CartDataMixin, FooterDataMixin, CategoriesDataMixin, TemplateView):
    template_name = "shop/vacancies.html"


class NotFound(CartDataMixin, FooterDataMixin, CategoriesDataMixin, TemplateView):
    template_name = "shop/404.html"


def not_found(request, exception=None):
    return NotFound().get(request)
