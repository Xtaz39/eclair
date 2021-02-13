from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Product,
    Category,
    ProductImage,
    Banner,
    PromotedProductsSettings,
    PromotedProductsManual,
    FooterSocial,
    ContactNumber,
    Address,
)
from .models import User


class ProductImageAdmin(admin.StackedInline):
    model = ProductImage


class PromotedProductsAdmin(admin.StackedInline):
    model = PromotedProductsManual


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
    inlines = [PromotedProductsAdmin]
    pass


class FooterSocialAdmin(admin.ModelAdmin):
    model = FooterSocial


class ContactsAdmin(admin.ModelAdmin):
    model = ContactNumber


class AddressAdmin(admin.ModelAdmin):
    model = Address


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(PromotedProductsSettings, PromotedProductsSettingsAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(FooterSocial, FooterSocialAdmin)
admin.site.register(ContactNumber, ContactsAdmin)
admin.site.register(Address, AddressAdmin)
