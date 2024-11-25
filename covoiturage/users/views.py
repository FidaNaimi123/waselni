from django.shortcuts import render

from django.shortcuts import render
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
import os
from django.template import TemplateDoesNotExist
from django.contrib.auth.hashers import make_password  # Ensure this import is at the top of the file
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
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
    # Supprimer 'user_id' de la session uniquement si elle existe
    if 'user_id' in request.session:
        del request.session['user_id']
        messages.success(request, "Déconnexion réussie.")

    if request.method == 'POST':
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Vérification des mots de passe
        if new_password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('update_password')

        # Validation de l'email
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Email invalide.")
            return redirect('update_password')

        try:
            # Récupérer l'utilisateur et vérifier les informations
            user = Users.objects.get(email=email)
            compte = Comptes.objects.get(user=user, phone=phone)

            # Mise à jour du mot de passe
            user.password = make_password(new_password)
            user.save()

            messages.success(request, "Mot de passe mis à jour avec succès.")

            # Envoi de l'email de notification
            try:
                send_mail(
                    subject='Initialisation de mot de passe réussie',
                    message=(
                        "Votre mot de passe a été réinitialisé avec succès.\n\n"
                        "Si vous n'avez pas demandé cette modification, veuillez contacter le support immédiatement."
                    ),
                    from_email='mohamedihsen81@gmail.com',
                    recipient_list=[email],
                )
                messages.success(request, "E-mail de notification envoyé avec succès.")
            except Exception as e:
                messages.error(request, f"Erreur lors de l'envoi de l'e-mail : {str(e)}")

            return redirect('index')

        except Users.DoesNotExist:
            messages.error(request, "Aucun utilisateur trouvé avec cet email.")
        except Comptes.DoesNotExist:
            messages.error(request, "Numéro de téléphone incorrect.")
        except Exception as e:
            messages.error(request, f"Une erreur inattendue est survenue : {str(e)}")

        return redirect('update_password')

    return render(request, 'Login/update_password.html')



def disconnect(request):
    logout(request)
    messages.success(request, "Déconnexion réussie.")
    return redirect('login')

def send_email(subject, message, from_email, recipient_list):
    # Envoi de l'email
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    except Exception as e:
        raise e
    

    ############################################# remembe me

from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from django.shortcuts import redirect, render

# Récupérer le modèle utilisateur personnalisé
User = get_user_model()

def connect_remember(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password', '')  # Le mot de passe peut être vide
        remember_me = request.POST.get('RememberMe', False)

        # Vérification : si "Remember Me" n'est pas coché, le mot de passe est obligatoire
        if not remember_me and not password:
            messages.error(request, "Le mot de passe est obligatoire si 'Remember Me' n'est pas coché.")
            return render(request, 'Login/index.html')

        try:
            # Recherche de l'utilisateur par email
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            messages.error(request, "Email incorrect. Veuillez réessayer.")
            return render(request, 'Login/index.html')

        # Authentification avec mot de passe
        if password:
            user_auth = authenticate(request, email=email, password=password)
            if user_auth:
                login(request, user_auth)
                messages.success(request, "Connexion réussie.")
                
                # Configurer la durée de session
                if remember_me:
                    request.session.set_expiry(60 * 60 * 24 * 30)  # 30 jours
                else:
                    request.session.set_expiry(0)  # Expire après fermeture du navigateur
                
                if hasattr(user, 'role') and user.role == "Administrateur":
                    return redirect('/admin/')
                return redirect('home1')

            else:
                messages.error(request, "Mot de passe incorrect. Veuillez réessayer.")
                return render(request, 'Login/index.html')

        # Connexion sans mot de passe (avec "Remember Me")
        if remember_me and not password:
            # Login manuel sans mot de passe
            login(request, user, backend=None)
            request.session.set_expiry(60 * 60 * 24 * 30)  # 30 jours
            messages.success(request, "Connexion réussie avec 'Remember Me'.")
            return redirect('home1')

    return render(request, 'Login/index.html')