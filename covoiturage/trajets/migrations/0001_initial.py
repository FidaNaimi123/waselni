# Generated by Django 4.2 on 2024-11-03 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Trajet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point_depart', models.CharField(max_length=100)),
                ('point_arrivee', models.CharField(max_length=100)),
                ('date_depart', models.DateField()),
                ('heure_depart', models.TimeField()),
                ('prix_par_place', models.DecimalField(decimal_places=2, max_digits=10)),
                ('places_disponibles', models.IntegerField()),
                ('statut', models.CharField(choices=[('actif', 'Actif'), ('complet', 'Complet'), ('annulé', 'Annulé')], max_length=20)),
                ('conducteur_nom_complet', models.CharField(max_length=200)),
                ('conducteur_contact', models.CharField(max_length=100)),
                ('matricule', models.CharField(max_length=20)),
            ],
        ),
    ]
