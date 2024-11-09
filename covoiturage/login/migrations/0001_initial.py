# Generated by Django 4.2 on 2024-11-03 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(default='default@gmail.com', max_length=50, unique=True)),
                ('password', models.CharField(max_length=128)),
            ],
        ),
    ]
