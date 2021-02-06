from django.contrib import admin

from .models import Product, Category


class AuthorAdmin(admin.ModelAdmin):
    pass


class CategoryAdmin(admin.ModelAdmin):
    pass


admin.site.register(Product, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
