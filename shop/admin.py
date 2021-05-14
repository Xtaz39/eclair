from django import forms
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
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


@admin.register(models.Product)
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


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("__str__", "menu_position")


@admin.register(models.Banner)
class BannerAdmin(admin.ModelAdmin):
    fields = ("image",)
    list_display = ("__str__", "priority")


@admin.register(models.PromotedProductsSettings)
class PromotedProductsSettingsAdmin(admin.ModelAdmin):
    inlines = [PromotedProductsAdmin]


@admin.register(
    models.FooterSocial,
    models.ContactNumber,
    models.Address,
    models.CakeDesign,
    models.CakeTopping,
    models.CakeDecor,
    models.CakePostcard,
)
class SimpleAdmin(admin.ModelAdmin):
    pass


@admin.register(models.User)
class UserAdmin(auth_admin.UserAdmin):
    pass
