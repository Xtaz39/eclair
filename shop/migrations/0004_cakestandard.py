# Generated by Django 3.1.7 on 2021-05-14 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0003_category_menu_position"),
    ]

    operations = [
        migrations.CreateModel(
            name="CakeStandard",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=100, verbose_name="Название")),
                (
                    "image",
                    models.ImageField(
                        upload_to="image/cake_standard/", verbose_name="Картинка"
                    ),
                ),
                (
                    "position",
                    models.PositiveIntegerField(unique=True, verbose_name="Позиция"),
                ),
            ],
            options={
                "verbose_name": "Торт стандартный",
                "verbose_name_plural": "Торты стандартные",
            },
        ),
    ]
