from django.db import models
from phone_field import PhoneField


class Product(models.Model):
    """Товар"""

    title = models.CharField("Название", max_length=100)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    price_discounted = models.DecimalField(
        "Цена после скидки", max_digits=10, decimal_places=2
    )
    description = models.TextField("Описание")
    filling = models.TextField("Начинка")
    topping = models.TextField("Декор")


class Customer(models.Model):
    """Пользователь"""

    name = models.CharField("Имя", max_length=50)
    phone = PhoneField("Номер телефона")
    email = models.CharField("Почта", max_length=50)
    birth = models.DateField("Дата рождения")


class DeliveryAddress:
    """Адрес доставки"""

    address = models.TextField("Адрес", max_length=150)
    customer = models.ForeignKey(to=Customer, on_delete=models.CASCADE)


class Cart(models.Model):
    """Корзина"""

    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    amount = models.IntegerField("Количество продукта", default=1)
    customer = models.ForeignKey(to=Customer, on_delete=models.CASCADE)


class Order(models.Model):
    """Заказ"""

    customer_name = models.CharField("Имя заказчика", max_length=100)
    phone = PhoneField("Номер телефона")
    address = models.TextField("Адрес", max_length=150)
    payment_type = models.CharField(
        "Способ оплаты",
        choices=(("cash", "Наличными"), ("card", "Картой на сайте")),
        max_length=100,
    )


class OrderProduct(models.Model):
    title = models.CharField("Название", max_length=100)
    category = models.CharField("Категория", max_length=100)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    amount = models.IntegerField("Количество продукта", default=1)
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING)
