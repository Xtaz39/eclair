# Generated by Django 3.1.7 on 2021-05-14 18:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0001_squashed_0032_auto_20210328_1455"),
    ]

    operations = [
        migrations.AlterField(
            model_name="address",
            name="name",
            field=models.CharField(max_length=255, verbose_name="Название точки"),
        ),
        migrations.AlterField(
            model_name="order",
            name="order_number",
            field=models.CharField(max_length=50, verbose_name="Номер заказа"),
        ),
        migrations.AlterField(
            model_name="order",
            name="session_id",
            field=models.CharField(max_length=100, verbose_name="Сессия"),
        ),
        migrations.AlterField(
            model_name="orderproduct",
            name="article",
            field=models.CharField(max_length=100, verbose_name="Артикул"),
        ),
        migrations.AlterField(
            model_name="orderproduct",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Дата покупки"),
        ),
        migrations.AlterField(
            model_name="promotedproductsmanual",
            name="promoted",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="shop.promotedproductssettings",
            ),
        ),
    ]