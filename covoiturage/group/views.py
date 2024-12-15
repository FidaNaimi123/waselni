from .models import *
import threading
from datetime import timedelta
from django.contrib.messages import add_message, INFO
from django.shortcuts import render, get_object_or_404, redirect
from .form import CarpoolForm  
from django.contrib import messages
from django.db.models import Q, Count
from users.models import Users # Assuming you are linking to the Django User model
from django.contrib.auth.forms import AuthenticationForm
from Notification.models import Notification  # Import the Notification model
from django.http import JsonResponse
from django.template.loader import render_to_string
from Reservations.models import Reservation
from collections import Counter
from .utils import generate_image_from_text
from django.core.files.base import ContentFile

def invitation_list(request):
    invitations = MembershipInvitation.objects.filter(user=request.user, status='invited')
    return render(request, 'group/invitation_list.html', {'invitations': invitations})



def invite_member(request, carpool_id):
    carpool = get_object_or_404(Carpool, id=carpool_id)
    if request.user != carpool.creator:
        messages.error(request, "Only the creator can invite members.")
        return redirect('carpool_detail', carpool_id=carpool_id)

    if request.method == 'POST':
        user_id = request.POST.get('user')
        user_to_invite = get_object_or_404(Users, id=user_id)

        # Create an invitation
        invitation, created = MembershipInvitation.objects.get_or_create(
            carpool=carpool,
            user=user_to_invite,
            defaults={'status': 'invited'}
        )

        if created:
            messages.success(request, f"Invitation sent to {user_to_invite.email}.")
        else:
            messages.warning(request, f"{user_to_invite.email} has already been invited.")

        return redirect('carpool_detail', carpool_id=carpool_id)

    users = Users.objects.exclude(id=request.user.id).exclude(id__in=carpool.members.values_list('id', flat=True))
    return render(request, 'group/invite_member.html', {'carpool': carpool, 'users': users})

def apply_to_join(request, carpool_id):
    carpool = get_object_or_404(Carpool, id=carpool_id)

    # Create an invitation for the user
    invitation, created = MembershipInvitation.objects.get_or_create(
        carpool=carpool,
        user=request.user,
        defaults={'status': 'pending'}
    )

    if created:
        messages.success(request, "Your application to join the carpool has been submitted.")
        
        # Create a notification for the carpool creator
        Notification.objects.create(
            type_notification='Application',
            message=f"{request.user.email} has applied to join {carpool.name}.",
            status_notification='sent',
            user=request.user,  # The user applying (sender)
            recipient=carpool.creator,  # The carpool creator (recipient)
            read=False
        )
        
    else:
        messages.warning(request, "You have already applied to join this carpool.")

    return redirect('carpool_detail', carpool_id=carpool_id)


def respond_to_invitation(request, invitation_id, response):
    invitation = get_object_or_404(MembershipInvitation, id=invitation_id)

    # Check if the user can respond to the invitation
    if request.user != invitation.user and request.user != invitation.carpool.creator:
        messages.error(request, "You cannot respond to this invitation.")
        return redirect('carpool_list')

    if response == 'accept':
        if request.user == invitation.user:
            # Users accepts their own invitation
            invitation.status = 'accepted'
            invitation.carpool.members.add(invitation.user)
            messages.success(request, "You have accepted the invitation to join the carpool.")

            # Create a notification for accepting the invitation
            Notification.objects.create(
                type_notification='Accept',
                message=f"{request.user.email} has accepted the invitation to join {invitation.carpool.name}.",
                status_notification='sent',
                user=request.user,  # The user accepting the invitation (sender)
                recipient=invitation.carpool.creator,  # The carpool creator (recipient)
                read=False
            )

        elif request.user == invitation.carpool.creator:
            # Group creator accepts a user's invitation to join
            invitation.status = 'accepted'
            invitation.carpool.members.add(invitation.user)
            messages.success(request, f"You have accepted {invitation.user.email}'s request to join the carpool.")

            # Create a notification for the user whose invitation is accepted
            Notification.objects.create(
                type_notification='Accept',
                message=f"Your request to join {invitation.carpool.name} has been accepted by {request.user.email}.",
                status_notification='sent',
                user=request.user,  # The group creator (sender)
                recipient=invitation.user,  # The invited user (recipient)
                read=False
            )

    elif response == 'decline':
        if request.user == invitation.user:
            # Users declines their own invitation
            invitation.status = 'declined'
            messages.success(request, "You have declined the invitation to join the carpool.")

            # Create a notification for declining the invitation
            Notification.objects.create(
                type_notification='Decline',
                message=f"{request.user.email} has declined the invitation to join {invitation.carpool.name}.",
                status_notification='sent',
                user=request.user,  # The user declining the invitation (sender)
                recipient=invitation.carpool.creator,  # The carpool creator (recipient)
                read=False
            )

        elif request.user == invitation.carpool.creator:
            # Group creator declines a user's invitation to join
            invitation.status = 'declined'
            messages.success(request, f"You have declined {invitation.user.email}'s request to join the carpool.")

            # Create a notification for the user whose invitation is declined
            Notification.objects.create(
                type_notification='Decline',
                message=f"Your request to join {invitation.carpool.name} has been declined by {request.user.email}.",
                status_notification='sent',
                user=request.user,  # The group creator (sender)
                recipient=invitation.user,  # The invited user (recipient)
                read=False
            )

    invitation.save()
    return redirect('carpool_detail', carpool_id=invitation.carpool.id)


def carpool_detail(request, carpool_id):
    # Fetch carpool by ID
    carpool = get_object_or_404(Carpool, id=carpool_id)
    
    # Get users who are not yet members of the carpool
    users = Users.objects.exclude(id__in=carpool.members.values_list('id', flat=True))

    # Get pending invitations for the carpool
    pending_invitations = MembershipInvitation.objects.filter(carpool=carpool, status='pending')

    # Fetch previous group reservations for the carpool's trip
    # Fetch group reservations for this carpool
    group_reservations = GroupRideReservation.objects.filter(carpool=carpool)

    # Fetch trips associated with the group reservations
    trips = Trajet.objects.filter(groupridereservation__in=group_reservations)

    # Fetch members of the carpool
    carpool_member_ids = carpool.members.values_list('id', flat=True)

    # Fetch individual reservations associated with these trips and carpool members
    previous_reservations = Reservation.objects.filter(
        trip_id__in=trips,
        user_id__in=carpool_member_ids
    ).order_by('reservation_date')
    
    # Calculate Most Frequent Destination from group reservations
    destinations = [reservation.trip.point_arrivee for reservation in group_reservations]
    most_frequent_destination = Counter(destinations).most_common(1)
    most_frequent_destination = most_frequent_destination[0] if most_frequent_destination else None

    # Get the list of individual reservations from the group reservations (finalized ones)

    if request.method == 'POST':
        if 'apply_to_join' in request.POST:
            # Logic for applying to join the carpool
            membership = MembershipInvitation.objects.create(user=request.user, carpool=carpool, status='pending')
            messages.success(request, "Your application to join the carpool has been sent.")
            return redirect('carpool_detail', carpool_id=carpool_id)
        
        elif 'member' in request.POST:
            # Logic for sending an invitation to a member
            member_id = request.POST['member']
            member = get_object_or_404(Users, id=member_id)
            # Add logic to send an invitation
            MembershipInvitation.objects.create(user=member, carpool=carpool, status='invited')
            messages.success(request, f"Invitation sent to {member.email}.")
            return redirect('carpool_detail', carpool_id=carpool_id)

    return render(request, 'group/carpool_detail.html', {
        'carpool': carpool,
        'users': users,
        'pending_invitations': pending_invitations,
        'previous_reservations': previous_reservations,
        'most_frequent_destination': most_frequent_destination
    })



def user_detail(request, user_id):
    user = get_object_or_404(Users, id=user_id)
    return render(request, 'group/user_detail.html', {'user': user})
# List view
def carpool_list(request):
    sort_by = request.GET.get('sort_by', '')
    filter_by = request.GET.get('filter_by', '')
    search_query = request.GET.get('search', '')
    
    # Apply filter and sort
    carpools = Carpool.objects.all()

    if filter_by and search_query:
        if filter_by == 'name':
            carpools = carpools.filter(name__icontains=search_query)
        elif filter_by == 'creator_name':
            carpools = carpools.filter(creator__email__icontains=search_query)
        elif filter_by == 'member_name':
            carpools = carpools.filter(members__email__icontains=search_query)
        elif filter_by == 'members_count':
            carpools = carpools.annotate(num_members=Count('members')).filter(num_members__gte=search_query)
    
    if sort_by == 'members_count':
        carpools = carpools.annotate(num_members=Count('members')).order_by('num_members')
    elif sort_by == 'creation_date':
        carpools = carpools.order_by('creation_date')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'html': render_to_string('group/carpool_list_cards.html', {'carpools': carpools,'user': request.user})})
    else :
        return render(request, 'group/carpool_list.html', {'carpools': carpools,'MEDIA_URL': settings.MEDIA_URL})



import os

def carpool_add(request):
    if request.method == 'POST':
        form = CarpoolForm(request.POST)
        if form.is_valid():
            carpool = form.save(commit=False)
            carpool.creator = request.user
            carpool.save()

            # Generate the image based on the group's name
            API_KEY = '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'
            url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large-turbo"

            headers = {
                "Authorization": f"Bearer {API_KEY}"
            }
            data = {
                "inputs": carpool.name,  # Use the carpool name as the prompt
            }

            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200 and response.headers['Content-Type'].startswith('image'):
                # Define your folder path inside MEDIA_ROOT
                media_folder = os.path.join(settings.MEDIA_ROOT, 'carpool_images')  
                
                # Automatically create the folder if it doesn't exist
                os.makedirs(media_folder, exist_ok=True)

                # Define the image name and path
                image_name = f"{carpool.name.replace(' ', '_')}_image.jpg"
                image_path = os.path.join(media_folder, image_name)

                # Save the image
                with open(image_path, "wb") as img_file:
                    img_file.write(response.content)

                # Save the relative image path in the Carpool instance
                carpool.image_path = os.path.join('carpool_images', image_name)  # Store relative path
                carpool.save()
            else:
                print(f"Image generation failed: {response.status_code}, {response.text}")

            return redirect('carpool_list')  # Redirect to a list view after saving
    else:
        form = CarpoolForm()

    return render(request, 'group/carpool_form.html', {'form': form})




# Edit view
def carpool_edit(request, pk):
    carpool = get_object_or_404(Carpool, pk=pk)
    if request.method == 'POST':
        form = CarpoolForm(request.POST, instance=carpool)
        if form.is_valid():
            form.save()
            return redirect('carpool_list')
    else:
        form = CarpoolForm(instance=carpool)
    return render(request, 'group/carpool_form.html', {'form': form})

# Delete view
def carpool_delete(request, pk):
    carpool = get_object_or_404(Carpool, pk=pk)
    
    # Check if the logged-in user is the creator of the carpool
    if carpool.creator != request.user:
        messages.error(request, "You do not have permission to delete this carpool.")
        return redirect('carpool_list')  # Change to your actual carpool list URL

    # If the user is the creator, proceed with deletion
    carpool.delete()
    messages.success(request, "Carpool deleted successfully.")
    return redirect('carpool_list')
 
def add_member(request, carpool_id):
    if request.method == "POST":
        carpool = get_object_or_404(Carpool, id=carpool_id)
        user_id = request.POST.get('member')
        user = get_object_or_404(Users, id=user_id)
        carpool.members.add(user)  # Adjust based on how you manage members
        messages.success(request, f'Users {user.email} has been added to the carpool.')
        return redirect('carpool_detail', carpool_id=carpool.id)

# Remove member from carpool
def remove_member(request, carpool_id, user_id):
    carpool = get_object_or_404(Carpool, id=carpool_id)
    user = get_object_or_404(Users, id=user_id)
    carpool.members.remove(user)  # Adjust based on how you manage members
    messages.warning(request, f'Users {user.email} has been removed from the carpool.')
    return redirect('carpool_detail', carpool_id=carpool.id)
# Create your views here.

def select_trip2(request):
    if request.method == 'POST':
        selected_trip_id = request.POST.get('select_trip2')
        return redirect('create_group_reservation', trip_id=selected_trip_id)
    return redirect('home1')

def create_group_reservation(request, trip_id):
    # Get the trip object
    trip = get_object_or_404(Trajet, id=trip_id)
    
    # Get all carpools where the user is a member or the creator
    carpools = Carpool.objects.filter(Q(members__in=[request.user]) | Q(creator=request.user))

    # If there's no carpool, handle the case
    if not carpools:
        return render(request, 'error.html', {'message': 'No carpool found for this user.'})
    
    for carpool in carpools:
        carpool.members_ids = carpool.members.values_list('id', flat=True)
        carpool.members_emails = carpool.members.values_list('email', flat=True)

    if request.method == 'POST':
        # Get the selected carpool
        selected_carpool_id = request.POST.get('selected_carpool')
        selected_carpool = get_object_or_404(Carpool, id=selected_carpool_id)

        # Get the selected members (exclude the user making the reservation)
        selected_members = request.POST.getlist('selected_members')

        # Limit the number of members to 4
        if len(selected_members) > 4:
            return render(request, 'error.html', {'message': 'You can select a maximum of 4 members.'})

        # Create a GroupReservation
        group_reservation = GroupRideReservation.objects.create(
            creator=request.user,
            trip=trip,
            carpool=selected_carpool  # Link to the selected carpool
        )
        # Automatically create a reservation for the creator
        Reservation.objects.create(
            user_id=request.user,
            trip_id=trip,
            seat_count=1,  # Assign a seat for the creator
            Payment_Method='cash_payment',  # Assuming payment method, can be adjusted
        )


        # Create GroupReservationParticipants for each selected member
        for user_id in selected_members:
            user = get_object_or_404(Users, id=user_id)
            ReservationParticipants.objects.create(
                group_reservation=group_reservation,
                user=user,
                status='pending'  # Set status as pending initially
            )

        # Redirect to the reservation confirmation page for the group
        return redirect('trajets_disponibles')

    # Pass the list of carpools to the template for the user to select from
    return render(request, 'group/create_group_reservation.html', {'trip': trip, 'carpools': carpools})




def send_notification(user, group_reservation):
    # Send a notification to each selected participant
    message = f"You have been invited to reserve a spot for the trip {group_reservation.trip.name}. Do you accept?"
    user.notification.create(message=message, reservation=group_reservation)  # Assuming a Notification model exists

def reservation_invitations(request):
    # Get all group reservations where the logged-in user is a participant with 'pending' status
    invitations = GroupRideReservation.objects.filter(
        reservationparticipants__user=request.user,
        reservationparticipants__status='pending'
    )

    return render(request, 'group/reservation_invitations.html', {'invitations': invitations})


def confirm_group_reservation(request, reservation_id):
    group_reservation = get_object_or_404(GroupRideReservation, id=reservation_id)

    # Check if the user is part of this reservation as a participant
    participant = group_reservation.reservationparticipants_set.filter(user=request.user).first()
    if not participant:
        return redirect('error')  # If the user is not part of the reservation

    if request.method == 'POST':
        action = request.POST.get('action')  # 'accept' or 'decline'
        if action == 'accept':
            participant.status = 'accepted'
             # Create individual reservation for the participant
            Reservation.objects.create(
                user_id=participant.user,
                trip_id=group_reservation.trip,
                seat_count=1,  # Assign a seat for the participant
                Payment_Method='cash_payment',  # Adjust payment method if necessary
            )
        elif action == 'decline':
            participant.status = 'declined'
        participant.save()

        return redirect('reservation_invitations')
    
    return render(request, 'group/confirm_group_reservation.html', {'group_reservation': group_reservation})

def finalize_reservation(group_reservation):
    accepted_participants = group_reservation.reservationparticipants_set.filter(status='accepted')

    for participant in accepted_participants:
        # Create a reservation for each accepted participant
        Reservation.objects.create(
            user=participant.user,
            trip=group_reservation.trip,
            seat_count=1,  # Assign a seat for the participant
            payment_method='cash_payment',  # Assuming payment method, can be adjusted
        )

    group_reservation.status = 'finalized'  # Mark the group reservation as finalized
    group_reservation.save()
    
def reservation_expiry(group_reservation):
    # Check if the reservation is expired (1 hour timeout)
    if timezone.now() > group_reservation.created_at + timedelta(hours=1):
        # Expire the reservation by changing the status of all participants to declined
        for participant in group_reservation.reservationparticipants_set.filter(status='pending'):
            participant.status = 'declined'
            participant.save()

        group_reservation.status = 'expired'
        group_reservation.save()
