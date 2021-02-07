from django.contrib import admin

from .models import Product, Category, ProductImage


class ProductImageAdmin(admin.StackedInline):
    model = ProductImage


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin]


class CategoryAdmin(admin.ModelAdmin):
    pass


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
