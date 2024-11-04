# Generated by Django 4.2 on 2024-10-06 21:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('Trip', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reservation_date', models.DateTimeField(auto_now_add=True)),
                ('Baggage', models.BooleanField(default=False)),
                ('seat_count', models.IntegerField()),
                ('status', models.CharField(choices=[('cancel', ' cancel'), ('on_hold', 'on_hold'), ('confirmed', 'confirmed')], max_length=20)),
                ('Payment_Method', models.CharField(choices=[(' online_payment', ' online_payment'), ('cash_payment', 'cash_payment')], max_length=20)),
                ('trip_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Trip.trip')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.users')),
            ],
            options={
                'unique_together': {('user_id', 'trip_id')},
            },
        ),
    ]
