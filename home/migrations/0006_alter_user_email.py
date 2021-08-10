# Generated by Django 3.2.5 on 2021-08-09 21:02

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_alter_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(default=None, max_length=254, null=True, unique=True, validators=[django.core.validators.EmailValidator()]),
        ),
    ]
