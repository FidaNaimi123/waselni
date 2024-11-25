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
import stripe
from django.conf import settings
from django.template.loader import render_to_string
from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from Notification.models import Notification
from datetime import timedelta , datetime
from django.utils.timezone import make_aware

from django.utils.timezone import now
from django.db import transaction  # Ensures atomicity for reservation and notifications
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
@csrf_exempt  # Pour ignorer la protection CSRF pour ce webhook spécifique
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET  # Remplacez par votre secret de webhook Stripe

    # Vérifiez la signature pour garantir que l'événement vient de Stripe
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Signature invalide
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Signature non vérifiée
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    # Traiter l'événement
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']  # Contient les informations de la session de paiement
        reservation_id = session['metadata']['reservation_id']  # Vous devez avoir stocké l'ID de la réservation dans les métadonnées

        # Trouver la réservation et mettre à jour le statut du paiement
        reservation = get_object_or_404(Reservation, id=reservation_id)
        reservation.payment_status = 'paid'
        reservation.payment_date = timezone.now()  # Ajoutez une date de paiement si nécessaire
        reservation.save()

        # Mettez à jour les places disponibles
        trip = reservation.trip_id
        trip.places_disponibles -= reservation.seat_count
        trip.save()

    # Répondez avec un 200 pour indiquer que tout s'est bien passé
    return JsonResponse({'status': 'success'}, status=200)
@login_required


@login_required
def create_reservation(request, trip_id): 
    trip = get_object_or_404(Trajet, id=trip_id)
    user = request.user

    # Vérifier si l'utilisateur a déjà réservé ce trajet
    if Reservation.objects.filter(user_id=user, trip_id=trip).exists():
        messages.error(request, 'Vous avez déjà réservé ce trajet.')
        return render(request, 'Reservations/create_reservation.html', {
            'form': ReservationForm(),
            'trip': trip,
        })

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():  # Ensure reservation and notifications are created together
                reservation = form.save(commit=False)
                reservation.trip_id = trip
                reservation.user_id = user

                # Validation du nombre de places
                if reservation.seat_count > trip.places_disponibles:
                    messages.error(request, f"Il n'y a pas assez de places disponibles. Places restantes : {trip.places_disponibles}")
                    return render(request, 'Reservations/create_reservation.html', {
                        'form': form,
                        'trip': trip,
                    })

                # Enregistrer la réservation sans la valider immédiatement
                reservation.save()

                # Si paiement en ligne, créer une session Stripe et rediriger vers la page de paiement
                if reservation.Payment_Method == 'online_payment':
                    YOUR_DOMAIN = "http://127.0.0.1:8000/"
                    try:
                        checkout_session = stripe.checkout.Session.create(
                            payment_method_types=['card'],
                            line_items=[{
                                'price_data': {
                                    'currency': 'usd',
                                    'product_data': {'name': f'Reservation for trip {trip.id}'},
                                    'unit_amount': int(trip.prix_par_place * reservation.seat_count * 100),  # En cents
                                },
                                'quantity': 1,
                            }],
                            mode='payment',
                            success_url=YOUR_DOMAIN + f'Reservations/payment-success/{reservation.id}/',
                            cancel_url=YOUR_DOMAIN + f'Reservations/payment-cancel/{reservation.id}/',
                            metadata={'reservation_id': reservation.id},  # Ajouter l'ID de la réservation aux métadonnées
                        )

                        # Retourner la redirection vers Stripe pour le paiement
                        return redirect(checkout_session.url, code=303)

                    except stripe.error.StripeError as e:
                        messages.error(request, f"Erreur lors de la création de la session de paiement : {str(e)}")
                        return redirect('create_reservation', trip_id=trip.id)

                # Si paiement hors ligne, mettre à jour les places disponibles et confirmer la réservation
                try:
                    # Décrémenter les places disponibles
                    trip.places_disponibles -= reservation.seat_count
                    trip.save()

                    reservation.save()  # Sauvegarder définitivement
                    send_reservation_email(reservation)

                    # Ajouter une notification de réservation
                    Notification.objects.create(
                        type_notification='Reservation',
                        message=f"Votre réservation pour le trajet le {trip.date_depart} à {trip.heure_depart} a été confirmée.",
                        status_notification='sent',
                        user=user,  # L'utilisateur qui a fait la réservation
                        recipient=user,  # L'utilisateur recevant la notification
                        read=False  # La notification est non lue par défaut
                    )

                    # Planifier une notification de rappel
                    reminder_time_naive = datetime.combine(trip.date_depart, trip.heure_depart)
                    reminder_time = make_aware(reminder_time_naive) - timedelta(minutes=10)          
                    if reminder_time > now():
                        Notification.objects.create(
                            type_notification='Reminder',
                            message=f"Rappel : Votre trajet commence bientôt, le {trip.date_depart} à {trip.heure_depart}.",
                            status_notification='pending',
                            user=user,  # L'utilisateur qui a fait la réservation
                            recipient=user,  # L'utilisateur recevant la notification
                            read=False  # La notification est non lue par défaut
                        )

                    messages.success(request, 'Votre réservation a été effectuée avec succès !')
                    return redirect('home1')  # Redirection après une réservation réussie
                except IntegrityError:
                    messages.error(request, 'Une erreur s\'est produite lors de la réservation.')
                    return render(request, 'Reservations/create_reservation.html', {
                        'form': form,
                        'trip': trip,
                    })
        else:
            messages.error(request, 'Il y a une erreur dans votre formulaire. Veuillez corriger les champs.')
    else:
        form = ReservationForm()

    return render(request, 'Reservations/create_reservation.html', {
        'form': form,
        'trip': trip,
    })

@login_required
def payment_success(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user_id=request.user)
    
    # Mettez à jour le statut du paiement
    reservation.payment_status = 'paid'
    reservation.save()

    # Mettre à jour les places disponibles après un paiement réussi
    trip = reservation.trip_id
    trip.places_disponibles -= reservation.seat_count
    trip.save()

    return render(request, 'Reservations/payment_sucess.html', {'reservation': reservation})

@login_required
def payment_cancel(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user_id=request.user)

    return render(request, 'Reservations/payment_cancel.html', {'reservation': reservation})


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
    trip = reservation.trip_id  # Trajet associé à la réservation
    old_seat_count = reservation.seat_count  # Ancien nombre de places réservées

    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            updated_reservation = form.save(commit=False)
            new_seat_count = updated_reservation.seat_count  # Nouvelle valeur des places

            # Calcul des places disponibles après ajustement
            available_seats = trip.places_disponibles + old_seat_count  # Restaurer les anciennes places dans le calcul
            if new_seat_count > available_seats:
                return render(request, 'Reservations/update_reservation.html', {
                    'form': form,
                    'reservation': reservation,
                    'error': f"Nombre de places insuffisant. Places disponibles : {trip.places_disponibles}.",
                })

            # Mise à jour des places disponibles
            trip.places_disponibles += old_seat_count  # Restaurer les anciennes places
            trip.places_disponibles -= new_seat_count  # Déduire les nouvelles places
            trip.save()

            updated_reservation.save()  # Sauvegarder la réservation mise à jour
            return redirect('home1')  # Redirection après mise à jour réussie
    else:
        form = ReservationForm(instance=reservation)

    return render(request, 'Reservations/update_reservation.html', {
        'form': form,
        'reservation': reservation,
    })

@login_required
def delete_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)  # Récupérer la réservation par son ID
    trip = reservation.trip_id  # Récupérer l'objet du trajet associé à la réservation

    if request.method == 'POST':
        # Créez une entrée dans la table Reservation_Historique avant la suppression
        Reservation_Historique.objects.create(
            user=reservation.user_id,  # Correspond à l'utilisateur de la réservation
            trajet=trip,  # Correspond au trajet de la réservation
            date_reservation=reservation.reservation_date,  # Date de création de la réservation
            nombre_places=reservation.seat_count,  # Nombre de places réservées
            baggage=reservation.Baggage,  # Indique si le bagage est inclus
            is_active=False,  # Historique marqué comme inactif
            date_annulation=now()  # Date et heure de la suppression
        )

        # Incrémenter le nombre de places disponibles pour le trajet
        trip.places_disponibles += reservation.seat_count  # Ajouter le nombre de places libérées
        trip.save()  # Sauvegarder le trajet après la mise à jour

        # Supprimer la réservation
        reservation.delete()

        # Rediriger vers la page d'accueil après la suppression
        return redirect('home')

    # Afficher la confirmation de suppression
    return render(request, 'Reservations/delete_reservation.html', {'reservation': reservation})

@login_required
def user_reservations(request):
    user = request.user
    today = timezone.now()

    # Récupérer les paramètres de recherche
    date_filter = request.GET.get('date', '')
    hour_filter = request.GET.get('hour', '')
    search_filter = request.GET.get('search', '')  # Un seul champ pour la recherche (départ ou arrivée)
    sort_order = request.GET.get('sort', '')  # Ajout pour récupérer l'ordre de tri
    # Filtrer les réservations valides
    reservations = Reservation.objects.filter(user_id=user)

    # Filtrage par date
    if date_filter:
        reservations = reservations.filter(trip_id__date_depart=date_filter)

    # Filtrage par heure
    if hour_filter:
        reservations = reservations.filter(trip_id__heure_depart__gte=hour_filter)


   # Appliquer le tri par date et heure
    if sort_order == 'asc':
        reservations = reservations.order_by('trip_id__date_depart', 'trip_id__heure_depart')
    elif sort_order == 'desc':
        reservations = reservations.order_by('-trip_id__date_depart', '-trip_id__heure_depart')
    # Filtrage par points de départ ou d'arrivée
    if search_filter:
        reservations = reservations.filter(
            Q(trip_id__point_depart__icontains=search_filter) | 
            Q(trip_id__point_arrivee__icontains=search_filter)
        )

    # Filtrage des réservations à venir
    reservations = reservations.filter(
        Q(trip_id__date_depart__gt=today.date()) |
        Q(trip_id__date_depart=today.date(), trip_id__heure_depart__gte=today.time())
    )

    # Gestion des réservations expirées
    expired_reservations = Reservation.objects.filter(user_id=user).filter(
        Q(trip_id__date_depart__lt=today.date()) |
        Q(trip_id__date_depart=today.date(), trip_id__heure_depart__lt=today.time())
    )

    # Archiver les réservations expirées
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