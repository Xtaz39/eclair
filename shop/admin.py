from django.contrib import admin

from .models import Product, Category, ProductImage, Banner


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


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Banner, BannerAdmin)
