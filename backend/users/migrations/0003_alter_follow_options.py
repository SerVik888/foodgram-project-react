# Generated by Django 3.2.16 on 2024-01-03 07:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_customuser_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'ordering': ('user',), 'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
    ]