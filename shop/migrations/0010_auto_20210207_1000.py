# Generated by Django 3.1.6 on 2021-02-07 10:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0009_auto_20210207_0833"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productimage",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="shop.product"
            ),
        ),
    ]
