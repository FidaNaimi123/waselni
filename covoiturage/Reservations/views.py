from django.shortcuts import render, redirect, get_object_or_404
from .models import Reservation, Trajet ,Reservation_Historique # Ensure these models are defined and imported correctly
from .ReservationForm import ReservationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from users.models import Users
from django.contrib import messages
from django.utils.timezone import now
from django.db import IntegrityError
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.db.models import Q



def list_trips(request):
    trips = Trajet.objects.all()  # Assuming Trajet is your trip model
    for trip in trips:
        print(trip.id, trip.destination, trip.departure_date)
    return render(request, 'Reservations/list_trips.html', {'trips': trips})

def select_trip(request):
    if request.method == 'POST':
        selected_trip_id = request.POST.get('selected_trip')
        return redirect('create_reservation', trip_id=selected_trip_id)
    return redirect('home1')

def home(request):
    return render(request, 'Home/index.html')
# Fonction pour envoyer un e-mail de confirmation
def send_reservation_email(reservation):
    subject = 'Confirmation de votre réservation'

    # Créer un message HTML avec un formatage amélioré
    message_html = render_to_string(
        'Reservations/reservation_confirmation.html',  # Template HTML à créer pour l'email
        {
            'reservation': reservation,
            'departure_point': reservation.trip_id.point_depart,
            'arrival_point': reservation.trip_id.point_arrivee,
            'departure_date': reservation.trip_id.date_depart,
            'departure_time': reservation.trip_id.heure_depart,
            'seat_count': reservation.seat_count,
            'has_baggage': 'Oui' if reservation.Baggage else 'Non',
        }
    )

    try:
        # Envoi de l'email en HTML et texte
        send_mail(
            subject,
            message_html,  # Le contenu HTML de l'email
            settings.DEFAULT_FROM_EMAIL,
            [reservation.user_id.email],
            fail_silently=False,
            html_message=message_html  # Ajout de l'option HTML
        )
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")  # Log de l'erreur
# Vue pour créer une réservation
@login_required
def create_reservation(request, trip_id):
    trip = get_object_or_404(Trajet, id=trip_id)
    user = request.user

    # Vérifier si l'utilisateur a déjà réservé ce trajet
    if Reservation.objects.filter(user_id=user, trip_id=trip).exists():
        return render(request, 'Reservations/create_reservation.html', {
            'form': ReservationForm(),
            'trip': trip,
            'error': 'Vous avez déjà réservé ce trajet.',
        })

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.trip_id = trip
            reservation.user_id = user
            try:
                reservation.save()
                send_reservation_email(reservation)
                return redirect('home1')  # Redirection après une réservation réussie
            except IntegrityError:
                return render(request, 'Reservations/create_reservation.html', {
                    'form': form,
                    'trip': trip,
                    'error': 'Une erreur s\'est produite lors de la réservation.',
                })
            
    else:
        form = ReservationForm()

    return render(request, 'Reservations/create_reservation.html', {
        'form': form,
        'trip': trip,
    })

def check_user(request):
    user_exists = None
    reservations = []
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = Users.objects.get(id=user_id)
            user_exists = True
            reservations = Reservation.objects.filter(user_id=user.id)
        except Users.DoesNotExist:
            user_exists = False
    return render(request, 'Reservations/check_user.html', {'user_exists': user_exists, 'reservations': reservations})

@login_required
def update_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            return redirect('home1')
    else:
        form = ReservationForm(instance=reservation)

    return render(request, 'Reservations/update_reservation.html', {'form': form, 'reservation': reservation})
@login_required
def delete_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)  # Récupérez la réservation par son ID

    if request.method == 'POST':
        # Créez une entrée dans la table Reservation_Historique avant la suppression
        Reservation_Historique.objects.create(
            user=reservation.user_id,  # Correspond à l'utilisateur de la réservation
            trajet=reservation.trip_id,  # Correspond au trajet de la réservation
            date_reservation=reservation.reservation_date,  # Date de création de la réservation
            nombre_places=reservation.seat_count,  # Nombre de places réservées
            baggage=reservation.Baggage,  # Indique si le bagage est inclus
            is_active=False,  # Historique marqué comme inactif
            date_annulation=now()  # Date et heure de la suppression
        )

        # Supprimer la réservation
        reservation.delete()

        # Redirigez vers la page d'accueil après la suppression
        return redirect('home')

    # Afficher la confirmation de suppression
    return render(request, 'Reservations/delete_reservation.html', {'reservation': reservation})
@login_required
def user_reservations(request):
    user = request.user
    today = timezone.now()

    # Récupérer les paramètres de recherche
    search = request.GET.get('search', '')
    date_filter = request.GET.get('date', '')
    hour_filter = request.GET.get('hour', '')

    # Filtrer les réservations valides : celles qui sont encore à venir ou aujourd'hui avec une heure dans le futur
    reservations = Reservation.objects.filter(user_id=user)
    
    if search:
        reservations = reservations.filter(trip_id__name__icontains=search)
    
    if date_filter:
        reservations = reservations.filter(trip_id__date_depart=date_filter)
    
    if hour_filter:
        reservations = reservations.filter(trip_id__heure_depart__gte=hour_filter)

    # Ajouter le filtrage de date pour les réservations futures ou à venir
    reservations = reservations.filter(
        trip_id__date_depart__gte=today.date()
    ) | reservations.filter(
        trip_id__date_depart=today.date(),
        trip_id__heure_depart__gte=today.time()
    )

    # Filtrer les réservations expirées : trajets dont la date et l'heure sont passées
    expired_reservations = Reservation.objects.filter(user_id=user)
    expired_reservations = expired_reservations.filter(
        trip_id__date_depart__lt=today.date()
    ) | expired_reservations.filter(
        trip_id__date_depart=today.date(),
        trip_id__heure_depart__lt=today.time()
    )

    # Enregistrer les réservations expirées dans l'historique et les supprimer
    for reservation in expired_reservations:
        Reservation_Historique.objects.create(
            user=reservation.user_id,
            trajet=reservation.trip_id,
            date_reservation=reservation.reservation_date,
            nombre_places=reservation.seat_count,
            baggage=reservation.Baggage,
            is_active=False,
            date_annulation=timezone.now(),
        )
        reservation.delete()

    # Passer les réservations valides au template
    return render(request, 'Reservations/user_reservations.html', {
        'user': user,
        'reservations': reservations,
        'today': today,
    })
@login_required
def afficher_historique(request):
    # Récupérer l'historique des réservations de cet utilisateur (les réservations expirées qui ont été enregistrées dans l'historique)
    historique_reservations = Reservation_Historique.objects.filter(user=request.user)

    # Passer l'historique des réservations au template
    context = {
        'historique_reservations': historique_reservations,
    }

    return render(request, 'Reservations/historique_reservations.html', context)


def test_email(request):
    try:
        send_mail(
            'Test d\'envoi d\'e-mail',
            'Ceci est un test pour vérifier l\'envoi d\'e-mails via Django.',
            settings.DEFAULT_FROM_EMAIL,
            ['fida.Naimi@esprit.tn'],  # Remplacez par une adresse de réception
            fail_silently=False,
        )
        return HttpResponse('E-mail envoyé avec succès.')
    except Exception as e:
        return HttpResponse(f'Erreur lors de l\'envoi de l\'e-mail : {e}')