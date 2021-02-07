from django.contrib import admin

from .models import Product, Category, ProductImage


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


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
