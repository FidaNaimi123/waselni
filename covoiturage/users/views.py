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
        photo = request.FILES.get('photo')  # Vérifie si une photo a été téléchargée

        # Validate that passwords match
        if password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'Login/registration.html', {'is_admin': is_admin})

        # Check if email is already used
        if Users.objects.filter(email=email).exists() or Comptes.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return render(request, 'Login/registration.html', {'is_admin': is_admin})
        # Si la photo n'est pas fournie, vous pouvez gérer ça ici
        if not photo:
            messages.error(request, "Veuillez télécharger une photo.")
            return render(request, 'Login/registration.html', {'is_admin': is_admin})

        # Hash the password and create user and account
        hashed_password = make_password(password)
        user = Users(email=email, password=hashed_password)
        user.save()

        compte = Comptes(fullname=fullname, email=email, phone=phone, password=hashed_password, user=user,photo=photo)
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

############################################# autre avec base 64
############################################# autre avec base 64
################################################# debut vue connaissance facial ####################################

import base64
import io
from django.shortcuts import render, get_object_or_404
#import face_recognition
from PIL import Image
from io import BytesIO
from django.core.exceptions import ImproperlyConfigured

from django.shortcuts import render
import base64
from io import BytesIO
from PIL import Image
#import face_recognition
#from .models import Comptes

import cv2
import numpy as np
import base64
from django.shortcuts import render, redirect
from django.contrib.auth import login


def facial_recognition(request):
    result = None
    error_message = None

    if request.method == "POST" and 'base64_image' in request.POST:
        base64_image_data = request.POST['base64_image']

        try:
            # Décoder l'image Base64
            image_data = base64.b64decode(base64_image_data)
            np_image = np.frombuffer(image_data, np.uint8)
            unknown_image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

            # Charger les visages connus
            known_encodings = []
            comptes = Comptes.objects.select_related('user').all()
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

            for c in comptes:
                if c.photo:  # Vérifier si le compte a une photo associée
                    compte_image_path = c.photo.path
                    known_image = cv2.imread(compte_image_path)
                    gray_known = cv2.cvtColor(known_image, cv2.COLOR_BGR2GRAY)

                    # Détecter les visages
                    faces = face_cascade.detectMultiScale(gray_known, scaleFactor=1.1, minNeighbors=5)
                    if len(faces) > 0:
                        x, y, w, h = faces[0]  # Premier visage détecté
                        face_encoding = gray_known[y:y+h, x:x+w]
                        known_encodings.append((c, face_encoding))

            # Détecter le visage dans l'image inconnue
            gray_unknown = cv2.cvtColor(unknown_image, cv2.COLOR_BGR2GRAY)
            faces_unknown = face_cascade.detectMultiScale(gray_unknown, scaleFactor=1.1, minNeighbors=5)

            if len(faces_unknown) > 0:
                x, y, w, h = faces_unknown[0]  # Premier visage détecté
                unknown_face = gray_unknown[y:y+h, x:x+w]

                # Comparer l'image donnée avec toutes les images connues
                for c, known_face in known_encodings:
                    if unknown_face.shape == known_face.shape:
                        mse = np.mean((unknown_face - known_face) ** 2)
                        if mse < 1000:  # Seuil ajustable pour correspondance
                            # Récupérer l'utilisateur associé
                            user = c.user
                            if user:
                                login(request, user)  # Authentifier l'utilisateur
                                return redirect('home1')  # Redirection après authentification

                # Si aucun visage ne correspond
                error_message = "Aucun visage correspondant n'a été trouvé."
            else:
                error_message = "Aucun visage n'a été détecté dans l'image donnée."

        except Exception as e:
            error_message = f"Une erreur est survenue : {str(e)}"

    return render(request, 'login/facial_recognition.html', {
        'result': result,
        'error_message': error_message,
    })


################################################### fin vue connaissance facial ########################################



################################################### la partie touche pour la connaissance facial ########################################

################################### index.html ###########################################################################################

################################### facial_recognition.html ###########################################################################################

################################### connaissance.css ###########################################################################################

################################### ajouter un dossier media meme niveau que group et notification etc ... ####################################

################################### registration model et html #################################################################
################################### urlsusers #################################################################