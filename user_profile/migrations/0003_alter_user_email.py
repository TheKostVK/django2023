# Generated by Django 4.2.11 on 2024-05-05 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0002_auto_20211129_0915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(error_messages={'unique': 'Адрес электронной почты должен быть уникальным'}, max_length=150, unique=True),
        ),
    ]