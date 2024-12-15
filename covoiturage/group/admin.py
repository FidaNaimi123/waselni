from django.contrib import admin
from .models import Carpool, GroupRideReservation, ReservationParticipants, MembershipInvitation
from django.utils.safestring import mark_safe
from django.contrib import messages
from users.models import Users


class UserInline(admin.TabularInline):
    """Inline for Carpool members"""
    model = Carpool.members.through  
    extra = 1  
    can_delete = True 


@admin.register(Carpool)
class CarpoolAdmin(admin.ModelAdmin):
    """Admin for Carpool management"""
    list_display = ['name', 'display_members', 'creator', 'creation_date']
    inlines = [UserInline]
    search_fields = ['name']
    filter_horizontal = ('members',)
    actions = ['add_member_action', 'remove_member_action']
    change_form_template = 'admin/group/carpool/change_form.html'

    def display_members(self, obj):
        """Displays members as clickable links in the admin list view."""
        members = obj.members.all()
        member_links = ', '.join([f'<a href="/admin/users/users/{m.id}/change/">{m.email}</a>' for m in members])
        return mark_safe(member_links) if members else 'No members'
    display_members.short_description = 'Members'

    def add_member_action(self, request, queryset):
        """Action to add a user to selected Carpools."""
        if 'apply' in request.POST:
            member_id = request.POST.get('member_id')
            try:
                member = Users.objects.get(pk=member_id)
                for carpool in queryset:
                    carpool.members.add(member)
                self.message_user(request, f"User {member.email} successfully added to selected carpools.", level=messages.SUCCESS)
            except Users.DoesNotExist:
                self.message_user(request, "User not found.", level=messages.ERROR)
        else:
            # Logic for confirmation page if needed
            pass
    add_member_action.short_description = 'Add member to selected carpools'

    def remove_member_action(self, request, queryset):
        """Action to remove a user from selected Carpools."""
        if 'apply' in request.POST:
            member_id = request.POST.get('member_id')
            try:
                member = Users.objects.get(pk=member_id)
                for carpool in queryset:
                    carpool.members.remove(member)
                self.message_user(request, f"User {member.email} successfully removed from selected carpools.", level=messages.SUCCESS)
            except Users.DoesNotExist:
                self.message_user(request, "User not found.", level=messages.ERROR)
        else:
            # Logic for confirmation page if needed
            pass
    remove_member_action.short_description = 'Remove member from selected carpools'


class GroupReservationParticipantsInline(admin.TabularInline):
    """Inline for GroupReservation participants."""
    model = ReservationParticipants
    extra = 1


@admin.register(GroupRideReservation)
class GroupReservationAdmin(admin.ModelAdmin):
    """Admin for Group Reservations"""
    list_display = ['carpool', 'trip', 'creator', 'reservation_date', 'reservation_deadline', 'is_expired']
    list_filter = ['reservation_date', 'reservation_deadline']
    search_fields = ['carpool__name', 'trip__name', 'creator__email']
    inlines = [GroupReservationParticipantsInline]

    def is_expired(self, obj):
        """Checks if the reservation deadline has expired."""
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


@admin.register(ReservationParticipants)
class GroupReservationParticipantsAdmin(admin.ModelAdmin):
    """Admin for managing Group Reservation Participants"""
    list_display = ['group_reservation', 'user', 'status']
    list_filter = ['status']
    search_fields = ['user__email', 'group_reservation__carpool__name']


@admin.register(MembershipInvitation)
class MembershipInvitationAdmin(admin.ModelAdmin):
    """Admin for managing Membership Invitations"""
    list_display = ['carpool', 'user', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['user__email', 'carpool__name']
