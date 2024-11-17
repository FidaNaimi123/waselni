from django.shortcuts import render, redirect, get_object_or_404
from .models import Reservation  # Ajoutez l'importation pour le modèle Reservation

from .models import Trajet  # Assurez-vous que ce modèle est défini
from .ReservationForm import ReservationForm
from users.models import Users
from django.utils import timezone
"""
def list_trips(request):
    trips = Trip.objects.all()  # Récupérer tous les trajets
    for trip in trips:
        print(trip.id, trip.destination, trip.departure_date)
    

    return render(request, 'Reservations/list_trips.html', {'trips': trips})


"""


def select_trip(request):
    if request.method == 'POST':
        selected_trip_id = request.POST.get('selected_trip')  # Récupérer l'ID du trajet sélectionné
        return redirect('create_reservation', trip_id=selected_trip_id)  # Redirigez vers la vue de création de réservation
    return redirect('home1')  # Redirigez vers la page d'accueil si la méthode n'est pas POST


def home(request):
    return render(request, 'home/home.html')  # Assurez-vous que le template 'home.html' existe




def create_reservation(request, trip_id):
    trip = get_object_or_404(Trajet, id=trip_id)  # Récupère le trajet sélectionné

    # Vérifiez si l'utilisateur est connecté
    if 'user_id' not in request.session:
        return redirect('connect')  # Redirige vers la page de connexion si non connecté

    # Récupérez l'utilisateur connecté
    user_id = request.session['user_id']
    user = get_object_or_404(Users, id=user_id)

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.trip_id = trip  # Associe le trajet sélectionné
            reservation.user_id = user  # Associe l'utilisateur connecté
            reservation.save()
            return redirect('home1')  # Redirige vers la page d'accueil

    else:
        form = ReservationForm()  # Formulaire vide en cas de méthode GET

    return render(request, 'Reservations/create_reservation.html', {'form': form, 'trip': trip})

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


def update_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)  # Récupérez la réservation par son ID

    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)  # Pré-remplir le formulaire avec l'instance de réservation
        if form.is_valid():
            form.save()  # Sauvegarder les modifications
            return redirect('home1')  # Redirigez vers une autre page après la mise à jour
    else:
        form = ReservationForm(instance=reservation)  # Pré-remplir le formulaire pour GET

    return render(request, 'Reservations/update_reservation.html', {'form': form, 'reservation': reservation})

def delete_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)  # Récupérez la réservation par son ID

    if request.method == 'POST':
        reservation.delete()  # Supprimer la réservation
        return redirect('home1')  # Redirigez vers une autre page après la suppression

    return render(request, 'Reservations/delete_reservation.html', {'reservation': reservation})

def user_reservations(request):
    # Vérifiez si l'utilisateur est connecté
    if 'user_id' not in request.session:
        return redirect('connect')  # Redirige vers la page de connexion si non connecté

    # Récupérez l'utilisateur connecté
    user_id = request.session['user_id']
    user = get_object_or_404(Users, id=user_id)

    # Récupérez les réservations associées à cet utilisateur
    reservations = Reservation.objects.filter(user_id=user)

    # Récupérez la date d'aujourd'hui
    today = timezone.now().date()

    # Passez la date d'aujourd'hui dans le contexte
    return render(request, 'Reservations/user_reservations.html', {
        'user': user,
        'reservations': reservations,
        'today': today  # La date d'aujourd'hui est incluse dans le contexte
    })