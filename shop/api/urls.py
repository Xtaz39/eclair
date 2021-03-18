from django.urls import path

from .views import Cart, AuthRequestCode, AuthLogin

urlpatterns = [
    path("cart", Cart.as_view(), name="cart"),
    path("auth/login", AuthLogin.as_view(), name="auth_request_code"),
    path("auth/request-code", AuthRequestCode.as_view(), name="auth_request_code"),
]
