from django.urls import path
from . import views

urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("p/<str:id>", views.Product.as_view(), name="product"),
    path("cake-order", views.CakeOrder.as_view(), name="cake-order"),
    path("about", views.About.as_view(), name="about"),
    path("contacts", views.Contacts.as_view(), name="contacts"),
    path("vacancies", views.Vacancies.as_view(), name="vacancies"),
    path("review", views.Review.as_view(), name="review"),
    path("news", views.News.as_view(), name="news"),
    path("news/<slug:slug>", views.NewsItem.as_view(), name="news-article"),
    path("cabinet", views.Cabinet.as_view(), name="cabinet"),
    path("cart", views.Cart.as_view(), name="cart"),
    path("checkout", views.Checkout.as_view(), name="checkout"),
]
