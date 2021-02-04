from django.db import models


class Product(models.Model):
    title = models.CharField(verbose_name="Название", max_length=100)
    price = models.DecimalField(verbose_name="Цена", max_digits=10, decimal_places=2)
    price_discounted = models.DecimalField(
        verbose_name="Цена после скидки", max_digits=10, decimal_places=2
    )
    description = models.TextField(verbose_name="Описание")
    filling = models.TextField(verbose_name="Начинка")
    topping = models.TextField(verbose_name="Декор")
