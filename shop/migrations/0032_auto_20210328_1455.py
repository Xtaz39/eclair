# Generated by Django 3.1.7 on 2021-03-28 11:55

from django.db import migrations
import phone_field.models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0031_auto_20210325_2117"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="phone",
            field=phone_field.models.PhoneField(
                blank=True,
                max_length=31,
                null=True,
                unique=True,
                verbose_name="Номер телефона",
            ),
        ),
    ]
