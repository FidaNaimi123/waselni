from django.contrib import admin
from .models import  Users
class UsersAdmin(admin.ModelAdmin):
    
    list_display = ('email', 'role')  

    
    search_fields = ('email', 'role')  

    
    list_per_page = 10 

    
    list_filter = ('role',)  

    
    

# Afficher un compteur d'utilisateurs
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['user_count'] = Users.objects.count()  # Compter les utilisateurs
        return super().changelist_view(request, extra_context=extra_context)




    
admin.site.register(Users)
