# Generated by Django 4.2 on 2024-11-10 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Notification', '0002_notification_read'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='type_notification',
            field=models.CharField(choices=[('info', 'Information'), ('warn', 'Warning'), ('alert', 'Alert'), ('Invitation', 'Invitation')], max_length=50),
        ),
    ]
