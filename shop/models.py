from django.db import models
from phone_field import PhoneField


class Product(models.Model):
    """Товар"""

    article = models.CharField("Артикул", max_length=15, primary_key=True)
    title = models.CharField("Название", max_length=100)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    price_discounted = models.DecimalField(
        "Цена после скидки",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    amount = models.PositiveIntegerField("Доступное количество")
    description = models.TextField("Описание")
    filling = models.TextField("Начинка")
    topping = models.TextField("Декор")
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.title} ({self.article})"

    @property
    def images_all(self):
        result = self.productimage_set.all()
        return [r.image for r in result]

    @property
    def image(self):
        return self.productimage_set.first().image


class ProductImage(models.Model):
    image = models.ImageField("Картинка", upload_to="image/product/")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Category(models.Model):
    """Категория продукта"""

    name = models.CharField("Имя", max_length=100)

    def __str__(self):
        return self.name

    @property
    def products(self):
        return list(self.product_set.all())


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

    product = models.ForeignKey(
        to=Product, on_delete=models.CASCADE, to_field="article"
    )
    amount = models.IntegerField("Количество продукта", default=1)
    customer = models.ForeignKey(to=Customer, on_delete=models.CASCADE)


class Order(models.Model):
    """Заказ"""

    # todo: change PK to not incrementing ID
    customer_name = models.CharField("Имя заказчика", max_length=100)
    phone = PhoneField("Номер телефона")
    address = models.TextField("Адрес", max_length=150)
    payment_type = models.CharField(
        "Способ оплаты",
        choices=(("cash", "Наличными"), ("card", "Картой на сайте")),
        max_length=100,
    )


class OrderProduct(models.Model):
    """Продукт из заказа"""

    title = models.CharField("Название", max_length=100)
    category = models.CharField("Категория", max_length=100)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    amount = models.IntegerField("Количество продукта", default=1)
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING)


class FooterSocial(models.Model):
    link = models.CharField("Ссылка на соцсеть", max_length=255)
    media_type = models.CharField(
        "Соцсеть",
        max_length=255,
        unique=True,
        choices=(
            ("instagram", "Инстаграмм"),
            ("facebook", "Фейсбук"),
            ("tiktok", "Тикток"),
            ("yotube", "Ютуб"),
            ("vk", "Вконтакте"),
            ("google_play", "Google Play"),
            ("app_store", "Apple Store"),
        ),
    )
