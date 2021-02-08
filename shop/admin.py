from django.contrib import admin

from .models import (
    Product,
    Category,
    ProductImage,
    Banner,
    PromotedProductsSettings,
    PromotedProductsManual,
)


class ProductImageAdmin(admin.StackedInline):
    model = ProductImage


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin]

    def get_readonly_fields(self, request, obj=None):
        if obj:  # when editing an object
            return ["article"]
        return self.readonly_fields


class CategoryAdmin(admin.ModelAdmin):
    pass


class BannerAdmin(admin.ModelAdmin):
    pass


class PromotedProductsSettingsAdmin(admin.ModelAdmin):
    pass


class PromotedProductsAdmin(admin.ModelAdmin):
    pass


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(PromotedProductsSettings, PromotedProductsSettingsAdmin)
admin.site.register(PromotedProductsManual, PromotedProductsAdmin)
