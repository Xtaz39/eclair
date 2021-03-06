# Generated by Django 3.1.7 on 2021-05-20 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0007_cakedesign_category"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomCakeDesignUploads",
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
                (
                    "image",
                    models.ImageField(
                        upload_to="image/cake_design_custom/%Y/%m/%d/",
                        verbose_name="Картинка",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now=True, verbose_name="Время загрузки"),
                ),
            ],
        ),
    ]
