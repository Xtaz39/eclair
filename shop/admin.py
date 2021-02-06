from django.contrib import admin

from .models import Product


class AuthorAdmin(admin.ModelAdmin):
    pass


admin.site.register(Product, AuthorAdmin)
