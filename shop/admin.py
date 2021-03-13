from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError

from . import models


class ProductImageAdmin(admin.StackedInline):
    model = models.ProductImage


class PromotedProductsAdmin(admin.StackedInline):
    model = models.PromotedProductsManual


class ProductForm(forms.ModelForm):
    def clean_recommendations(self):
        data = self.cleaned_data["recommendations"]
        if data and len(data) < 4:
            raise ValidationError("Нужно выбрать не менее 4 товаров.")

        return data


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin]
    form = ProductForm

    def get_readonly_fields(self, request, obj=None):
        if obj:  # when editing an object
            return ["article"]
        return self.readonly_fields

    def get_object(self, request, object_id, from_field=None):
        # hack to pass obj_id to formfield_for_manytomany
        self._obj_id = object_id
        return super().get_object(request, object_id, from_field)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if hasattr(self, "_obj_id") and db_field.name == "recommendations":
            kwargs["queryset"] = db_field.remote_field.model.objects.exclude(
                article=self._obj_id
            )

        return super().formfield_for_manytomany(db_field, request, **kwargs)


class CategoryAdmin(admin.ModelAdmin):
    pass


class BannerAdmin(admin.ModelAdmin):
    pass


class PromotedProductsSettingsAdmin(admin.ModelAdmin):
    inlines = [PromotedProductsAdmin]
    pass


class FooterSocialAdmin(admin.ModelAdmin):
    model = models.FooterSocial


class ContactsAdmin(admin.ModelAdmin):
    model = models.ContactNumber


class AddressAdmin(admin.ModelAdmin):
    model = models.Address


class CakeDesignAdmin(admin.ModelAdmin):
    model = models.CakeDesign


class CakeToppingAdmin(admin.ModelAdmin):
    model = models.CakeTopping


class CakeDecorAdmin(admin.ModelAdmin):
    model = models.CakeDecor


class CakePostcardAdmin(admin.ModelAdmin):
    model = models.CakePostcard


admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Banner, BannerAdmin)
admin.site.register(models.PromotedProductsSettings, PromotedProductsSettingsAdmin)
admin.site.register(models.User, UserAdmin)
admin.site.register(models.FooterSocial, FooterSocialAdmin)
admin.site.register(models.ContactNumber, ContactsAdmin)
admin.site.register(models.Address, AddressAdmin)
admin.site.register(models.CakeDesign, CakeDesignAdmin)
admin.site.register(models.CakeTopping, CakeToppingAdmin)
admin.site.register(models.CakePostcard, CakePostcardAdmin)
admin.site.register(models.CakeDecor, CakeDecorAdmin)
