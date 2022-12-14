# Generated by Django 4.1.2 on 2022-11-12 21:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Team",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "logo",
                    models.ImageField(
                        default="default/no_image.jpg", upload_to="teams/logos/"
                    ),
                ),
                ("name", models.CharField(max_length=30)),
                ("short_name", models.CharField(blank=True, max_length=3, null=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("bio", models.TextField(blank=True, null=True)),
                (
                    "balance",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=12),
                ),
                ("country", django_countries.fields.CountryField(max_length=2)),
                (
                    "profile_pic",
                    models.ImageField(blank=True, null=True, upload_to="profiles/"),
                ),
                (
                    "fav_team",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.team",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Player",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nickname", models.CharField(max_length=30)),
                ("name", models.CharField(max_length=30)),
                ("nationality", django_countries.fields.CountryField(max_length=2)),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        default="default/no_image.jpg",
                        null=True,
                        upload_to="players/images/",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.team",
                    ),
                ),
            ],
            options={
                "ordering": ["team", "name"],
            },
        ),
    ]
