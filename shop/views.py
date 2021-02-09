from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from .models import (
    Product as ProductModel,
    Category as CategoryModel,
    Banner as BannerModel,
    PromotedProductsSettings,
    PromotedProductsManual,
)


class TopMenuDataMixin:
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["categories"] = CategoryModel.objects.exclude(product=None).all()
        return data


class Index(TemplateView):
    template_name = "shop/index/index.html"

    def _get_promoted_products(self) -> list[ProductModel]:
        promoted_settings: PromotedProductsSettings = (
            PromotedProductsSettings.objects.first()
        )
        if not promoted_settings:
            return []

        limit = promoted_settings.limit
        if promoted_settings.mode == "auto":
            return ProductModel.objects.all()[:limit]

        if promoted_settings.mode == "manual":
            pm = PromotedProductsManual.objects.select_related("product").all()[:limit]
            return [p.product for p in pm]

        return []

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        categories = (
            CategoryModel.objects.prefetch_related(
                "product_set", "product_set__productimage_set"
            )
            .exclude(product=None)
            .all()
        )
        data["categories"] = categories
        data["banner"] = BannerModel.objects.order_by("priority").first()
        data["promoted_products"] = self._get_promoted_products()

        return data


class Product(TopMenuDataMixin, TemplateView):
    template_name = "shop/product.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        article = data["article"]
        product = get_object_or_404(
            ProductModel.objects.prefetch_related("productimage_set"),
            article=article,
        )
        data["product"] = product
        return data


class Cabinet(TopMenuDataMixin, TemplateView):
    template_name = "shop/cabinet.html"


class About(TopMenuDataMixin, TemplateView):
    template_name = "shop/about.html"


class CakeOrder(TopMenuDataMixin, TemplateView):
    template_name = "shop/cake-order.html"


class Contacts(TopMenuDataMixin, TemplateView):
    template_name = "shop/contacts.html"


class News(TopMenuDataMixin, TemplateView):
    template_name = "shop/news.html"


class NewsItem(TopMenuDataMixin, TemplateView):
    template_name = "shop/news-item.html"


class Cart(TopMenuDataMixin, TemplateView):
    template_name = "shop/cart.html"


class Checkout(TopMenuDataMixin, TemplateView):
    template_name = "shop/checkout.html"


class Review(TopMenuDataMixin, TemplateView):
    template_name = "shop/review.html"


class Vacancies(TopMenuDataMixin, TemplateView):
    template_name = "shop/vacancies.html"


class NotFound(TopMenuDataMixin, TemplateView):
    template_name = "shop/404.html"


def not_found(request, exception=None):
    return NotFound().get(request)
