from django.shortcuts import render, redirect, get_object_or_404
from .models import Trajet
from .forms import TrajetForm,WeatherForm
from django.utils import timezone
from django.http import JsonResponse
#import requests
from django.db.models import Count, Sum
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render
from .models import Trajet
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse



from reportlab.lib import colors

from django.shortcuts import render
from deepface import DeepFace
import base64
import cv2
import numpy as np
from django.http import JsonResponse

from reportlab.lib import colors
import requests

import requests

def get_weather_with_region(region):
    """
    Appelle l'API WeatherAPI pour obtenir les conditions météorologiques actuelles avec une région spécifique.
    Associe les conditions météo à des icônes correspondantes.
    """
    import requests  # Import nécessaire pour exécuter les requêtes
    country = "Tunisia"  # Pays constant
    api_key = "c619229cc9dc4f308e8173048240812"  # Remplacez par votre clé API valide
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={region},{country}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()

        # Extraire les informations principales
        temperature = weather_data["current"]["temp_c"]
        condition = weather_data["current"]["condition"]["text"]

        # Associer condition à une icône
        if "rain" in condition.lower():
            icon = "🌧️"  # Pluie
        elif "cloud" in condition.lower():
            icon = "🌥️"  # Nuages dispersés (nouvelle icône)
        elif "clear" in condition.lower() or "sunny" in condition.lower():
            icon = "☀️"  # Ensoleillé
        elif "snow" in condition.lower():
            icon = "❄️"  # Neige
        elif "storm" in condition.lower():
            icon = "⛈️"  # Orage
        else:
            icon = "🌤️"  # Temps par défaut (partiellement nuageux)

        # Retourner les données sous forme de dictionnaire
        return {
            "region": region,
            "country": country,
            "temp": temperature,
            "condition": condition,
            "icon": icon,  # Ajouter l'icône correspondante
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Erreur lors de la récupération des données météo : {e}"
        }


def confirmation_weather(request):
    if request.method == 'POST':
        form = WeatherForm(request.POST)
        if form.is_valid():
            
            point_depart = form.cleaned_data['point_depart']
            point_arrivee = form.cleaned_data['point_arrivee']
            
            # Appel de la fonction pour récupérer les données météo
            weather_depart = get_weather_with_region(point_depart)
            weather_arrivee = get_weather_with_region(point_arrivee)
            
            context = {
                'weather_depart': weather_depart,
                'weather_arrivee': weather_arrivee,
                'form': form,
            }
            return render(request, 'Trip/confirmation_weather.html', context)
        else:
            print("Form invalid:", form.errors)  # Affiche les erreurs du formulaire dans la console
    else:
        form = WeatherForm()  # Crée un nouveau formulaire vide

    return render(request, 'Trip/weather.html', {'form': form})

def creer_trajet(request):
    if request.method == 'POST':
        form = TrajetForm(request.POST)
        if form.is_valid():
            form.save()  # Enregistre le trajet dans la base de données
            point_depart = form.cleaned_data['point_depart']
            point_arrivee = form.cleaned_data['point_arrivee']
            
            # Appel de la fonction pour récupérer les données météo
            weather_depart = get_weather_with_region(point_depart)
            weather_arrivee = get_weather_with_region(point_arrivee)
            
            context = {
                'weather_depart': weather_depart,
                'weather_arrivee': weather_arrivee,
                'form': form,
            }
            return render(request, 'Trip/confirmation_weather.html', context)
        else:
            print("Form invalid:", form.errors)  # Affiche les erreurs du formulaire dans la console
    else:
        form = TrajetForm()  # Crée un nouveau formulaire vide
   
    return render(request, 'Trip/creer_trajet.html', {'form': form})
def liste_trajets(request):
    # Récupérer les trajets de base
    trajets = Trajet.objects.all().order_by('date_depart', 'heure_depart')

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

    # Obtenir la date actuelle
    today = timezone.now().date()  # Obtenez uniquement la date, sans l'heure

    # Ajouter un filtre pour n'afficher que les trajets avec une date de départ à partir d'aujourd'hui
    trajets = trajets.filter(date_depart__gte=today)

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

    # Trier les trajets par date de départ
    trajets = trajets.order_by('date_depart', 'heure_depart')
    return render(request, 'Trip/trajets_disponibles.html', {
        'trajets': trajets,
        'point_depart': point_depart,
        'point_arrivee': point_arrivee,
        'date_depart': date_depart
    })

  




def afficher_carte(request):
    if request.method == 'POST':
        start_point = request.POST.get('start_point')  # Point de départ saisi par l'utilisateur
        end_point = request.POST.get('end_point')      # Point d'arrivée saisi par l'utilisateur
        return render(request, 'Trip/afficher_carte.html', {
            'start_point': start_point,
            'end_point': end_point
        })
    return render(request, 'Trip/afficher_carte.html')




def statistiques_view(request):
    # Fetch statistics
    total_trajets = Trajet.objects.count()
    trajets_annules = Trajet.objects.filter(statut='annulé').count()
    revenue_total = Trajet.objects.aggregate(Sum('prix_par_place'))['prix_par_place__sum'] or 0

    # Calculate non-annulés trajets
    trajets_non_annules = total_trajets - trajets_annules

    # Calculate percentages
    pourcentage_annules = (trajets_annules / total_trajets * 100) if total_trajets > 0 else 0
    pourcentage_effectues = (trajets_non_annules / total_trajets * 100) if total_trajets > 0 else 0

    # Optional: Add average revenue per trajet
    revenu_moyen = revenue_total / total_trajets if total_trajets > 0 else 0

    # Pass all stats as context
    stats = {
        'total_trajets': total_trajets,
        'trajets_annules': trajets_annules,
        'trajets_non_annules': trajets_non_annules,
        'revenue_total': revenue_total,
        'pourcentage_annules': round(pourcentage_annules, 2),
        'pourcentage_effectues': round(pourcentage_effectues, 2),
        'revenu_moyen': round(revenu_moyen, 2),
    }
    return render(request, 'Trip/statistiques.html', {'stats': stats})
    





def export_trajets(request):
    # Créer une réponse HTTP pour le fichier PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="liste_trajets.pdf"'
    
    # Créer un objet canvas pour générer le PDF
    p = canvas.Canvas(response, pagesize=letter)
    
    # Récupérer les trajets
    trajets = Trajet.objects.all()
    
    # Ajouter un titre
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 750, "Liste des Trajets")
    
    # Ajouter la date de génération
    p.setFont("Helvetica", 10)
    p.drawString(400, 735, "Date de génération : " + timezone.now().strftime('%d-%m-%Y %H:%M:%S'))

    # Ajouter les en-têtes de colonne
    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(colors.white)
    p.rect(50, 700, 500, 20, fill=1)  # Rectangle pour l'en-tête avec couleur de fond
    p.setFillColor(colors.black)
    p.drawString(60, 705, "Point de Départ")
    p.drawString(160, 705, "Point d'Arrivée")
    p.drawString(260, 705, "Date de Départ")
    p.drawString(360, 705, "Heure de Départ")
    p.drawString(460, 705, "Prix par Place")
    
    # Ajouter les données des trajets avec des couleurs et bordures
    y_position = 680  # Position de départ pour afficher les trajets
    p.setFont("Helvetica", 10)
    
    for i, trajet in enumerate(trajets):
        # Alternance des couleurs des lignes
        if i % 2 == 0:
            p.setFillColor(colors.beige)  # Couleur de fond pour les lignes paires
        else:
            p.setFillColor(colors.white)  # Couleur de fond pour les lignes impaires
        
        # Dessiner un rectangle pour chaque ligne
        p.rect(50, y_position-10, 500, 20, fill=1)
        
        # Dessiner le texte pour chaque colonne
        p.setFillColor(colors.black)
        p.drawString(60, y_position, trajet.point_depart)
        p.drawString(160, y_position, trajet.point_arrivee)
        p.drawString(260, y_position, str(trajet.date_depart))
        p.drawString(360, y_position, str(trajet.heure_depart))
        p.drawString(460, y_position, f"{trajet.prix_par_place} DT")
        
        # Ajouter une bordure autour de chaque cellule
        p.setStrokeColor(colors.black)
        p.rect(50, y_position-10, 110, 20)  # Point de départ
        p.rect(160, y_position-10, 100, 20)  # Point d'arrivée
        p.rect(260, y_position-10, 100, 20)  # Date de départ
        p.rect(360, y_position-10, 100, 20)  # Heure de départ
        p.rect(460, y_position-10, 90, 20)   # Prix par place
        
        y_position -= 20  # Déplacer la position vers le bas pour la ligne suivante
        
        # Ajouter une nouvelle page si nécessaire
        if y_position < 60:
            p.showPage()  # Créer une nouvelle page
            y_position = 750  # Remise à zéro de la position Y pour la nouvelle page
            p.setFont("Helvetica-Bold", 10)
            p.setFillColor(colors.white)
            p.rect(50, 700, 500, 20, fill=1)  # Rectangle pour l'en-tête
            p.setFillColor(colors.black)
            p.drawString(60, 705, "Point de Départ")
            p.drawString(160, 705, "Point d'Arrivée")
            p.drawString(260, 705, "Date de Départ")
            p.drawString(360, 705, "Heure de Départ")
            p.drawString(460, 705, "Prix par Place")
            y_position -= 20
    
    # Sauvegarder le PDF
    p.showPage()
    p.save()

    return response
from django.http import JsonResponse
from django.shortcuts import render
from deepface import DeepFace
import cv2
import numpy as np

# Points attribués par émotion
POINTS_PAR_EMOTION = {
    "happy": 10,
    "sad": -8,
    "angry": -10,
    "surprise": -2,
    "neutral": 8,
    "fear": -5,
    "disgust": -1
}

# Seuils pour les badges
BADGES = {
    50: " Bronze",
    100: " Argent",
    200: " Or"
}

def emotion_from_camera(request):
    if request.method == "POST" and request.FILES.get('image'):
        image_data = request.FILES['image']
        
        # Lire l'image dans OpenCV
        img_array = np.frombuffer(image_data.read(), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            return JsonResponse({'error': 'Erreur de décodage de l\'image'}, status=400)
        
        # Analyser les émotions avec DeepFace
        try:
            result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
            
            if not result:
                return JsonResponse({'error': 'Aucune émotion détectée'}, status=400)
            
            # Récupérer l'émotion dominante
            dominant_emotion = result[0]['dominant_emotion']
            score = POINTS_PAR_EMOTION.get(dominant_emotion, 0)

            # Calcul du score total et attribution du badge
            total_score = request.session.get('total_score', 0) + score
            request.session['total_score'] = total_score

            badge = None
            for threshold, badge_name in sorted(BADGES.items()):
                if total_score >= threshold:
                    badge = badge_name

            return JsonResponse({
                'emotion': dominant_emotion,
                'score': score,
                'total_score': total_score,
                'badge': badge
            })
        
        except Exception as e:
            return JsonResponse({'error': f"Erreur d'analyse : {str(e)}"}, status=500)
    
    return render(request, 'Trip/reconnaissance_emotionnelle.html')


import joblib
import os
from django.conf import settings
import pandas as pd

# Charger le modèle
MODEL_PATH = os.path.join(settings.BASE_DIR, 'Trip', 'ml_models', 'ride_price_model_full.pkl')
model = joblib.load(MODEL_PATH)

# Charger les colonnes d'origine
model_columns = model.feature_names_in_

def prediction_prix(request):
    if request.method == "POST":
        # Récupérer les données du formulaire
        lieu_depart = request.POST.get("lieu_depart")
        lieu_arrivee = request.POST.get("lieu_arrivee")
        distance = float(request.POST.get("distance"))
        duree = float(request.POST.get("duree"))
        type_trajet = request.POST.get("type_trajet")

        # Encoder les données
        input_data = pd.DataFrame([{
            "distance": distance,
            "duree": duree,
            "type_trajet_Confort": 1 if type_trajet == "Confort" else 0,
            "type_trajet_Premium": 1 if type_trajet == "Premium" else 0,
            # Assurez-vous de traiter les valeurs de lieu_arrivee ici
        }])

        # Ajouter les colonnes manquantes (par exemple, les lieux d'arrivée)
        for col in model_columns:
            if col not in input_data.columns:
                input_data[col] = 0  # Ajoutez des colonnes avec des valeurs par défaut (par exemple, 0)

        # Réorganiser les colonnes pour correspondre à celles du modèle
        input_data = input_data[model_columns]

        # Prédire le prix
        prix_pred = model.predict(input_data)[0]

        return JsonResponse({"prix_pred": round(prix_pred, 2)})

    return render(request, "Trip/formulaire_prediction.html")
