from django.shortcuts import render, redirect, get_object_or_404
from .models import Trajet
from .forms import TrajetForm
from django.utils import timezone
from django.http import JsonResponse
#import requests
from django.db.models import Count, Sum
from django.db.models import Sum


def creer_trajet(request):
    if request.method == 'POST':
        form = TrajetForm(request.POST)
        if form.is_valid():
            form.save()  # Enregistre le trajet dans la base de données
            return redirect('liste_trajets')  # Redirige vers la liste des trajets après création
        else:
            print("Form invalid:", form.errors)  # Affiche les erreurs du formulaire dans la console
    else:
        form = TrajetForm()  # Crée un nouveau formulaire vide
   
    return render(request, 'Trip/creer_trajet.html', {'form': form})

def liste_trajets(request):
    # Récupérer les trajets de base
    trajets = Trajet.objects.all().order_by('date_depart')
    today = timezone.now().date()  # Date actuelle

    # Récupérer les critères de recherche
    point_depart = request.GET.get('point_depart', '').strip()
    point_arrivee = request.GET.get('point_arrivee', '').strip()
    date_depart = request.GET.get('date_depart', '').strip()

    # Appliquer les filtres si des critères sont fournis
    if point_depart:
        trajets = trajets.filter(point_depart__icontains=point_depart)
    if point_arrivee:
        trajets = trajets.filter(point_arrivee__icontains=point_arrivee)
    if date_depart:
        trajets = trajets.filter(date_depart=date_depart)

    # Mettre à jour le statut si nécessaire
    for trajet in trajets:
        if trajet.places_disponibles == 0:
            trajet.statut = 'complet'  # Change le statut à 'complet'
            trajet.save()
        elif trajet.places_disponibles > 0 and trajet.statut not in ['actif', 'annulé']:
            trajet.statut = 'actif'  # Change le statut à 'actif'
            trajet.save()

    return render(request, 'Trip/liste_trajets.html', {
        'trajets': trajets,
        'today': today,
        'point_depart': point_depart,
        'point_arrivee': point_arrivee,
        'date_depart': date_depart
    })



def modifier_trajet(request, trajet_id):
    trajet = get_object_or_404(Trajet, id=trajet_id)  # Récupère le trajet à modifier

    if request.method == 'POST':
        form = TrajetForm(request.POST, instance=trajet)  # Lier le formulaire à l'instance du trajet
        if form.is_valid():
            form.save()  # Enregistre les modifications
            return redirect('liste_trajets')  # Redirige vers la liste des trajets
    else:
        form = TrajetForm(instance=trajet)  # Remplit le formulaire avec les données existantes

    return render(request, 'Trip/modifier_trajet.html', {'form': form, 'trajet': trajet})


def supprimer_trajet(request, trajet_id):
    trajet = get_object_or_404(Trajet, id=trajet_id)  # Récupère le trajet à supprimer
    trajet.delete()  # Supprime le trajet de la base de données
    return redirect('liste_trajets')  # Redirige vers la liste des trajets



def trajets_disponibles(request):
    # Par défaut, obtenir tous les trajets actifs avec des places disponibles
    trajets = Trajet.objects.filter(places_disponibles__gt=0, statut='actif')

    # Récupérer les critères de recherche
    point_depart = request.GET.get('point_depart', '').strip()
    point_arrivee = request.GET.get('point_arrivee', '').strip()
    date_depart = request.GET.get('date_depart', '').strip()

    # Appliquer les filtres si des critères sont fournis
    if point_depart or point_arrivee or date_depart:
        if point_depart:
            trajets = trajets.filter(point_depart__icontains=point_depart)
        if point_arrivee:
            trajets = trajets.filter(point_arrivee__icontains=point_arrivee)
        if date_depart:
            trajets = trajets.filter(date_depart=date_depart)
    trajets = trajets.order_by('date_depart') 
    return render(request, 'Trip/trajets_disponibles.html', {
        'trajets': trajets,
        'point_depart': point_depart,
        'point_arrivee': point_arrivee,
        'date_depart': date_depart
    })
  


def afficher_carte(request, id):  # L'argument doit être 'id'
    trajet = get_object_or_404(Trajet, id=id)  # Utilisez 'id' ici pour récupérer le trajet
    start_point = trajet.point_depart
    end_point = trajet.point_arrivee
    return render(request, 'Trip/afficher_carte.html', {'start_point': start_point, 'end_point': end_point})




def statistiques_view(request):
    # Fetch statistics
    total_trajets = Trajet.objects.count()
    trajets_annules = Trajet.objects.filter(statut='annulé').count()
    revenue_total = Trajet.objects.aggregate(Sum('prix_par_place'))['prix_par_place__sum'] or 0

    # Calculate non-annulés trajets
    trajets_non_annules = total_trajets - trajets_annules

    # Pass all stats as context
    stats = {
        'total_trajets': total_trajets,
        'trajets_annules': trajets_annules,
        'trajets_non_annules': trajets_non_annules,
        'revenue_total': revenue_total,
    }

    return render(request, 'Trip/statistiques.html', {'stats': stats})
