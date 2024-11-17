from django.contrib import admin
from .models import Carpool, GroupRideReservation, RideReservationParticipants
from django.contrib import admin
from .models import Carpool, GroupRideReservation, RideReservationParticipants
from django.utils.safestring import mark_safe
from django.contrib import messages
from users.models import Users
class UserInline(admin.TabularInline):
    model = Carpool.members.through  
    extra = 1  
    can_delete = True 

@admin.register(Carpool)
class CarpoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_members'] 
    inlines = [UserInline] 
    search_fields = ['name']  
    filter_horizontal = ('members',)  
    actions = ['add_member_action', 'remove_member_action']
    change_form_template = 'admin/group/carpool/change_form.html'

    def save_model(self, request, obj, form, change):
        
        super().save_model(request, obj, form, change)
    
    
    def display_members(self, obj):
        members = obj.members.all()
        member_links = ', '.join([f'<a href="/admin/auth/user/{m.id}/change/">{m.username}</a>' for m in members])
        return mark_safe(member_links) if members else 'No members'
    display_members.short_description = 'Members'

    def add_member_action(self, request, queryset):
        if 'apply' in request.POST:
            member_id = request.POST.get('member_id')
            try:
                member = Users.objects.get(pk=member_id)
                for carpool in queryset:
                    carpool.members.add(member)
                self.message_user(request, f"Users {member.username} successfully added to selected carpools.", level=messages.SUCCESS)
            except Users.DoesNotExist:
                self.message_user(request, "Users not found.", level=messages.ERROR)
        else:
            # Implement a confirmation page logic here if needed
            pass

    def remove_member_action(self, request, queryset):
        if 'apply' in request.POST:
            member_id = request.POST.get('member_id')
            try:
                member = Users.objects.get(pk=member_id)
                for carpool in queryset:
                    carpool.members.remove(member)
                self.message_user(request, f"Users {member.username} successfully removed from selected carpools.", level=messages.SUCCESS)
            except Users.DoesNotExist:
                self.message_user(request, "Users not found.", level=messages.ERROR)
        else:
            # Implement a confirmation page logic here if needed
            pass

    add_member_action.short_description = 'Add member to selected carpools'
    remove_member_action.short_description = 'Remove member from selected carpools'
    
    class GroupRideReservationInline(admin.TabularInline):
        model = GroupRideReservation
        extra = 1 

    inlines = [GroupRideReservationInline]

@admin.register(GroupRideReservation)
class GroupRideReservationAdmin(admin.ModelAdmin):
    list_display = ('group', 'reservation_date', 'accept_as_group')
    list_filter = ('reservation_date', 'accept_as_group')
    search_fields = ('group__name',)

@admin.register(RideReservationParticipants)
class RideReservationParticipantsAdmin(admin.ModelAdmin):
    list_display = ('group_ride_reservation', 'user', 'status')
    list_filter = ('status',)
    search_fields = ('user__username', 'group_ride_reservation__group__name')


