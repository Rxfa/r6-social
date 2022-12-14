# Generated by Django 4.1.2 on 2022-11-12 21:45

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="player",
            name="nationality",
            field=django_countries.fields.CountryField(
                blank=True, max_length=2, null=True
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="country",
            field=django_countries.fields.CountryField(
                blank=True, max_length=2, null=True
            ),
        ),
    ]
