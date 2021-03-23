from django.urls import path

from .views import Cart, AuthRequestCode, ConfirmCode

urlpatterns = [
    path("cart", Cart.as_view(), name="cart"),
    path("confirm-action", ConfirmCode.as_view(), name="confirm_action"),
    path("request-code", AuthRequestCode.as_view(), name="request_code"),
]
