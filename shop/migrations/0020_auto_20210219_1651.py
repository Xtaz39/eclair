# Generated by Django 3.1.6 on 2021-02-19 16:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0019_auto_20210219_1649"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="category",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="shop.category",
                verbose_name="Категория",
            ),
        ),
    ]
