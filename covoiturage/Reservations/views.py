from django.shortcuts import render, redirect, get_object_or_404
from .models import Reservation, Trajet  # Ensure these models are defined and imported correctly
from .ReservationForm import ReservationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from users.models import Users
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

@login_required  # Ensure only authenticated users can access this view
def create_reservation(request, trip_id):
    trip = get_object_or_404(Trajet, id=trip_id)

    # Use request.user to get the logged-in user
    user = request.user

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.trip_id = trip  # Associate the selected trip
            reservation.user_id = user  # Associate the logged-in user
            reservation.save()
            return redirect('home1')

    else:
        form = ReservationForm()

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
    reservation = get_object_or_404(Reservation, id=reservation_id)

    if request.method == 'POST':
        reservation.delete()
        return redirect('home1')

    return render(request, 'Reservations/delete_reservation.html', {'reservation': reservation})

@login_required
def user_reservations(request):
    user = request.user
    reservations = Reservation.objects.filter(user_id=user)
    today = timezone.now().date()

    return render(request, 'Reservations/user_reservations.html', {
        'user': user,
        'reservations': reservations,
        'today': today
    })
