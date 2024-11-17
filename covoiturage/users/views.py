from django.shortcuts import render

from django.shortcuts import render
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
import os
from django.template import TemplateDoesNotExist
from django.contrib.auth.hashers import make_password  # Ensure this import is at the top of the file

from users.models import  Users
from django.contrib.auth import authenticate, login, logout
from registration.models import   Comptes
from django.contrib import messages


def index(request):
    return render(request, 'Login/index.html')

    
    

def registration(request):
    is_admin = False
    is_logged_in = request.user.is_authenticated  # Simplified check for authentication

    if is_logged_in:
        user = request.user
        if user.role == "Administrateur":
            is_admin = True

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        fullname = request.POST.get('fullname')
        phone = request.POST.get('phone')

        # Validate that passwords match
        if password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'Login/registration.html', {'is_admin': is_admin})

        # Check if email is already used
        if Users.objects.filter(email=email).exists() or Comptes.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return render(request, 'Login/registration.html', {'is_admin': is_admin})

        # Hash the password and create user and account
        hashed_password = make_password(password)
        user = Users(email=email, password=hashed_password)
        user.save()

        compte = Comptes(fullname=fullname, email=email, phone=phone, password=hashed_password, user=user)
        compte.save()

        messages.success(request, "Votre compte a été créé avec succès ! Vous pouvez maintenant vous connecter.")
        return redirect('index')

    return render(request, 'Login/registration.html', {'is_admin': is_admin})



def connect(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Connexion réussie.")
            if user.role == "Administrateur":
                return redirect('/admin/')
            return redirect('home1')
        else:
            messages.error(request, "Email ou mot de passe incorrect.")

    return render(request, 'Login/index.html')



def update_password(request):
    if 'user_id' in request.session:
        del request.session['user_id']
        messages.success(request, "Déconnexion réussie.")

    if request.method == 'POST':
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Validate password match
        if new_password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('update_password')

        try:
            user = Users.objects.get(email=email)
            compte = Comptes.objects.get(user=user, phone=phone)

            # Update password
            user.password = make_password(new_password)
            user.save()

            messages.success(request, "Mot de passe mis à jour avec succès.")
            return redirect('index')

        except (Users.DoesNotExist, Comptes.DoesNotExist):
            messages.error(request, "Email ou téléphone incorrect.")
            return redirect('update_password')

    return render(request, 'Login/update_password.html')



def liste_users(request):
    listeusers = Users.objects.all()
    return render(request, 'Login/liste_user.html', {'listeusers': listeusers})



def supprimer_utilisateur(request, id_utilisateur):
    try:
        user = Users.objects.get(id=id_utilisateur)
        user.delete()
        messages.success(request, "Utilisateur supprimé avec succès.")
    except Users.DoesNotExist:
        messages.error(request, "Utilisateur introuvable!")

    return redirect('liste_users')




def continuer(request):
    if request.user.is_authenticated:
        return render(request, 'Home/index.html')
    else:
        messages.error(request, "Vous devez être connecté pour accéder à cette page.")
        return redirect('connect')




def disconnect(request):
    logout(request)
    messages.success(request, "Déconnexion réussie.")
    return redirect('login')