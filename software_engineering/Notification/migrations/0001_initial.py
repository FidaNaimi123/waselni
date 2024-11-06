# Generated by Django 4.2 on 2024-11-03 16:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id_notification', models.AutoField(primary_key=True, serialize=False)),
                ('type_notification', models.CharField(choices=[('info', 'Information'), ('warn', 'Warning'), ('alert', 'Alert')], max_length=50)),
                ('message', models.TextField()),
                ('status_notification', models.CharField(choices=[('sent', 'Sent'), ('pending', 'Pending'), ('failed', 'Failed')], max_length=50)),
                ('date_sent', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
