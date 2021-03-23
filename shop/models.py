from __future__ import annotations

import datetime
import random

import pendulum
from django.contrib.auth.models import AbstractUser
from django.db import models
from phone_field import PhoneField

from shop import validators


class User(AbstractUser):
    phone = PhoneField("Номер телефона", null=True, blank=True)
    birthday = models.DateField("День рождения", null=True, blank=True)


class ConfirmCode(models.Model):
    id = models.CharField("ID", max_length=50, primary_key=True)
    phone = PhoneField("Номер телефона")
    code = models.TextField("Код проверки", max_length=50)
    action = models.CharField("Действие", max_length=50)
    created_at = models.DateTimeField("Время создания", auto_now=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField("Дата рождения", null=True, blank=True)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"


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
    filling = models.TextField("Начинка", null=True, blank=True)
    topping = models.TextField("Декор", null=True, blank=True)
    category = models.ForeignKey(
        "Category", verbose_name="Категория", on_delete=models.SET_NULL, null=True
    )
    recommendations = models.ManyToManyField("self", blank=True, symmetrical=False)
    iiko_id = models.CharField(
        "ID IIKO", max_length=50, unique=True, null=True, blank=True
    )

    def __str__(self):
        return f"{self.title} ({self.article})"

    @property
    def images_all(self):
        result = self.productimage_set.all()
        return [r.image for r in result]

    @property
    def image(self):
        img = self.productimage_set.first()
        if img is None:
            return ProductImage()
        return img.image

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"


class ProductImage(models.Model):
    image = models.ImageField("Картинка", upload_to="image/product/")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Картинка продукта"
        verbose_name_plural = "Картинки продуктов"


class Category(models.Model):
    """Категория продукта"""

    name = models.CharField("Имя", max_length=100)

    def __str__(self):
        return self.name

    @property
    def products(self):
        return list(self.product_set.all())

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Customer(models.Model):
    """Пользователь"""

    name = models.CharField("Имя", max_length=50)
    phone = PhoneField("Номер телефона")
    email = models.CharField("Почта", max_length=50)
    birth = models.DateField("Дата рождения")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class DeliveryAddress:
    """Адрес доставки"""

    address = models.TextField("Адрес", max_length=150)
    customer = models.ForeignKey(to=Customer, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Адрес доставки"
        verbose_name_plural = "Адреса доставки"


class CartProduct(models.Model):
    """Корзина"""

    product = models.ForeignKey(
        to=Product, on_delete=models.CASCADE, to_field="article"
    )
    session_id = models.CharField("Сессия", max_length=100, null=True)
    amount = models.IntegerField("Количество продукта", default=1)
    customer = models.ForeignKey(to=Customer, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class Order(models.Model):
    """Заказ"""

    order_number = models.CharField("Номер заказа", max_length=50)
    customer_name = models.CharField("Имя заказчика", max_length=100)
    phone = PhoneField("Номер телефона")
    address = models.TextField("Адрес", max_length=150)
    payment_type = models.CharField(
        "Способ оплаты",
        choices=(("cash", "Наличными"), ("card", "Картой на сайте")),
        max_length=100,
    )
    session_id = models.CharField("Сессия", max_length=100)

    @staticmethod
    def generate_order_number():
        date = datetime.date.today().strftime("%y%m%d")
        number = random.randint(100000, 999999)
        return f"{date}-{number}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderProduct(models.Model):
    """Продукт из заказа"""

    article = models.CharField("Артикул", max_length=100)
    title = models.CharField("Название", max_length=100)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    amount = models.PositiveIntegerField("Количество продукта", default=1)
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField("Дата покупки", auto_now_add=True)

    class Meta:
        verbose_name = "Продукт из заказа"
        verbose_name_plural = "Продукты из заказа"


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
            ("youtube", "Ютуб"),
            ("vk", "Вконтакте"),
            ("google_play", "Google Play"),
            ("app_store", "Apple Store"),
        ),
    )

    def __str__(self):
        return self.media_type.title().replace("_", " ")

    class Meta:
        verbose_name = "Соцсеть"
        verbose_name_plural = "Соцсети"


class Banner(models.Model):
    title = models.CharField("Заголовок", max_length=100, null=True, blank=True)
    text = models.TextField("Текст", null=True, blank=True)
    image = models.ImageField("Картинка", upload_to="image/product/")
    button_text = models.CharField("Текст кнопки", max_length=50, null=True, blank=True)
    button_url = models.CharField(
        "Ссылка на кноке", max_length=255, null=True, blank=True
    )
    priority = models.SmallIntegerField("Приоритет", unique=True)

    def __str__(self):
        if not self.title:
            return f"Баннер ({self.priority})"

        return f"{self.title} ({self.priority})"

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"


class PromotedProductsSettings(models.Model):
    mode = models.CharField(
        "Режим",
        max_length=100,
        choices=(
            ("manual", "ручной"),
            ("auto", "автоматичесский"),
        ),
    )
    title = models.CharField("Заголовок промо", max_length=100)
    period = models.CharField(
        "Промежуток времени",
        max_length=100,
        choices=(
            ("week_this", "эта неделя"),
            ("week_last", "прошлая неделя"),
            ("month_this", "этот месяц"),
            ("month_last", "прошлый месяц"),
            ("year_half_this", "последние пол года"),
            ("year_this", "текущий год"),
        ),
        null=True,
        blank=True,
    )
    limit = models.PositiveSmallIntegerField(
        "Максимальное количество товаров",
        null=True,
        blank=True,
    )

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = "Настройка промо"
        verbose_name_plural = "Настройки промо"

    def get_period_interval(self):
        dt = pendulum.now()
        if self.period == "week_this":
            return dt.start_of("week"), dt

        elif self.period == "week_last":
            last_week = dt.subtract(weeks=1)
            return last_week.start_of("week"), last_week.end_of("week")

        elif self.period == "month_this":
            return dt.start_of("month"), dt

        elif self.period == "month_last":
            month_last = dt.subtract(weeks=1)
            return month_last.start_of("month"), month_last.end_of("month")

        elif self.period == "year_half_this":
            return dt.subtract(6).start_of("month"), dt

        elif self.period == "year_this":
            return dt.start_of("year"), dt


class PromotedProductsManual(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    promoted = models.ForeignKey(PromotedProductsSettings, on_delete=models.CASCADE)
    priority = models.PositiveSmallIntegerField("Приоритет", unique=True)

    def __str__(self):
        return f"{self.product.title} ({self.priority})"

    class Meta:
        verbose_name = "Промо ручная настройка"
        verbose_name_plural = "Промо ручная настройка"


class ContactNumber(models.Model):
    number = PhoneField("Номер телефона", null=True, blank=True)

    def __str__(self):
        return str(self.number)

    class Meta:
        verbose_name = "Телефон"
        verbose_name_plural = "Телефоны"


class Address(models.Model):
    name = models.CharField("Название точки", max_length=255)
    location = models.CharField("Адрес", max_length=255)
    work_hours = models.CharField("Время работы", max_length=50)
    coordinates = models.CharField(
        "Координаты",
        max_length=50,
        validators=[validators.is_coordinates],
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"

    def __str__(self):
        return f"{self.name} ({self.location})"


class CakeDesign(models.Model):
    title = models.CharField("Название", max_length=100)
    image = models.ImageField("Картинка", upload_to="image/cake/")

    class Meta:
        verbose_name = "Торт на заказ дизайн"
        verbose_name_plural = "Торт на заказ (дизайн)"

    def __str__(self):
        return self.title


class CakeTopping(models.Model):
    title = models.CharField("Название", max_length=100)
    image = models.ImageField("Картинка", upload_to="image/cake/")

    class Meta:
        verbose_name = "Торт на заказ начинка"
        verbose_name_plural = "Торт на заказ (начинка)"

    def __str__(self):
        return self.title


class CakeDecor(models.Model):
    title = models.CharField("Название", max_length=100)
    image = models.ImageField("Картинка", upload_to="image/cake/")

    class Meta:
        verbose_name = "Торт на заказ декор"
        verbose_name_plural = "Торт на заказ (декор)"

    def __str__(self):
        return self.title


class CakePostcard(models.Model):
    title = models.CharField("Название", max_length=100)
    image = models.ImageField("Картинка", upload_to="image/cake/")

    class Meta:
        verbose_name = "Торт на заказ открытка"
        verbose_name_plural = "Торт на заказ (открытка)"

    def __str__(self):
        return self.title
