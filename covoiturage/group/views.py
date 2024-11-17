from .models import Carpool,MembershipInvitation
from django.shortcuts import render, get_object_or_404, redirect
from .form import CarpoolForm  
from django.contrib import messages
from django.db.models import Q, Count
from users.models import Users # Assuming you are linking to the Django User model
from django.contrib.auth.forms import AuthenticationForm
from Notification.models import Notification  # Import the Notification model

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
    carpool = get_object_or_404(Carpool, id=carpool_id)
    users = Users.objects.exclude(id__in=carpool.members.values_list('id', flat=True))  # Users not already members

    # Get pending invitations for the carpool
    pending_invitations = MembershipInvitation.objects.filter(carpool=carpool, status='pending')

    if request.method == 'POST':
        if 'apply_to_join' in request.POST:
            # Logic for applying to join the carpool
            membership = MembershipInvitation.objects.create(user=request.user, carpool=carpool, status='pending')
            messages.success(request, "Your application to join the carpool has been sent.")
            return redirect('carpool_detail', carpool_id=carpool_id)
        
        elif 'member' in request.POST:
            # Logic for sending an invitation
            member_id = request.POST['member']
            member = get_object_or_404(Users, id=member_id)
            # Add logic to send an invitation
            MembershipInvitation.objects.create(user=member, carpool=carpool, status='invited')
            messages.success(request, f"Invitation sent to {member.email}.")
            return redirect('carpool_detail', carpool_id=carpool_id)

    return render(request, 'group/carpool_detail.html', {
        'carpool': carpool,
        'users': users,
        'pending_invitations': pending_invitations,  # Pass pending invitations to the template
    })


def user_detail(request, user_id):
    user = get_object_or_404(Users, id=user_id)
    return render(request, 'group/user_detail.html', {'user': user})
# List view
def carpool_list(request):
    query = request.GET.get('search', '')
    member_count = request.GET.get('member_count', '')

    # Apply filters based on search and member count
    carpools = Carpool.objects.all()
    if query:
        carpools = carpools.filter(Q(name__icontains=query) | Q(members__email__icontains=query)).distinct()
    if member_count:
        carpools = carpools.annotate(member_count=Count('members')).filter(member_count__gte=member_count)

    return render(request, 'group/carpool_list.html', {'carpools': carpools, 'search_query': query, 'member_count': member_count})

# Add view
def carpool_add(request):
    if request.method == 'POST':
        form = CarpoolForm(request.POST)
        if form.is_valid():
            carpool = form.save(commit=False)  # Create the Carpool instance without saving to the database yet
            carpool.creator = request.user  # Set the creator to the current user
            carpool.save()  # Now save the instance to the database
            return redirect('carpool_list')
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
