# Generated by Django 5.0.4 on 2024-04-09 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_user_last_login'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='completed',
            field=models.BooleanField(default=False),
        ),
    ]