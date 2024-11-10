from django.shortcuts import render

from django.shortcuts import render
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
import os
from django.template import TemplateDoesNotExist
from users.models import  Users
from registration.models import   Comptes
from django.contrib import messages
from django.contrib.auth.hashers import make_password  # Pour le hashage du mot de passe
from django.contrib.auth.hashers import check_password  # Pour vérifier le hash du mot de passe


def index(request):
    
    
        return render(request, 'Login/index.html')
    
    

def registration(request):
    is_admin = False  # Par défaut, on suppose que l'utilisateur n'est pas administrateur
    is_logged_in = 'user_id' in request.session  # Vérifie si l'utilisateur est connecté

    if is_logged_in:
        try:
            # Récupère l'utilisateur connecté
            user = Users.objects.get(id=request.session['user_id'])
            if user.role == "Administrateur":  # Vérifiez si le rôle de l'utilisateur est "Administrateur"
                is_admin = True  # Si oui, on définit is_admin à True
        except Users.DoesNotExist:
            # Si l'utilisateur n'existe pas dans la base de données, il a probablement été supprimé.
            del request.session['user_id']  # Supprimer l'ID de session pour éviter toute erreur future
            messages.error(request, "Utilisateur introuvable, veuillez vous reconnecter.")
            return redirect('connect')  # Rediriger vers la page de connexion

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        fullname = request.POST.get('fullname')
        phone = request.POST.get('phone')
        

        # Vérification si les mots de passe correspondent
        if password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'Login/registration.html', {'is_admin': is_admin})

        # Vérification si l'email est déjà utilisé dans Utilisateurs ou Comptes
        if Users.objects.filter(email=email).exists() or Comptes.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return render(request, 'Login/registration.html', {'is_admin': is_admin})

        # Hashage du mot de passe
        hashed_password = make_password(password)

        # Créer un nouvel utilisateur
        user = Users(email=email, password=hashed_password)
        user.save()

        # Créer un compte associé
        compte = Comptes(fullname=fullname, email=email, phone=phone, password=hashed_password, user=user)
        compte.save()

        # Afficher un message de succès
        messages.success(request, "Votre compte a été créé avec succès ! Vous pouvez maintenant vous connecter.")
        return redirect('index')  # Redirige vers la page de connexion

    return render(request, 'Login/registration.html', {'is_admin': is_admin})  # Afficher le formulaire pour ajouter un compte

def connect(request):
    # Initialiser les variables
    is_logged_in = False
    is_admin = False
    
    # Vérification si l'utilisateur est déjà connecté
    if 'user_id' in request.session:
        is_logged_in = True
        try:
            user = Users.objects.get(id=request.session['user_id'])
            if user.role == "Administrateur":  # Vérification du rôle
                is_admin = True
        except Users.DoesNotExist:
            del request.session['user_id']  # Si l'utilisateur n'existe pas, déconnexion automatique

    # Traitement du formulaire de connexion
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Recherche de l'utilisateur par son email
            user = Users.objects.get(email=email)

            # Vérification du mot de passe
            if check_password(password, user.password):
                # Connexion réussie, on stocke l'ID de l'utilisateur dans la session
                request.session['user_id'] = user.id
                messages.success(request, "Connexion réussie.")
                
                # Vérification du rôle de l'utilisateur après connexion
                if user.role == "Administrateur":
                    return redirect('/admin/')  # Redirection vers l'interface d'administration de Django
                else:
                    return redirect('home1')  # Rediriger vers la page d'accueil pour les utilisateurs normaux
            else:
                messages.error(request, "Mot de passe incorrect.")
        except Users.DoesNotExist:
            messages.error(request, "Aucun utilisateur trouvé avec cet email.")

    return render(request, 'Login/index.html', {'is_logged_in': is_logged_in, 'is_admin': is_admin})


def update_password(request):
    # Supprimer l'utilisateur de la session
    if 'user_id' in request.session:
        del request.session['user_id']
        messages.success(request, "Déconnexion réussie.")
        
    if request.method == 'POST':
        email = request.POST['email']
        phone = request.POST['phone']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        # Vérification si les mots de passe correspondent
        if new_password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('update_password')

        try:
            # Vérifier si l'utilisateur existe dans les tables User et Compte
            user = Users.objects.get(email=email)
            compte = Comptes.objects.get(user =user, phone = phone)

            # Si l'utilisateur existe, mettre à jour son mot de passe
            user.password = make_password(new_password)  # Hasher le mot de passe
            user.save()

            messages.success(request, "Mot de passe mis à jour avec succès.")
            return redirect('index')  # Rediriger vers la page de connexion après succès

        except (Users.DoesNotExist, Comptes.DoesNotExist):
            messages.error(request, "Email ou téléphone incorrect.")
            return redirect('update_password')

    return render(request, 'Login/update_password.html')


def liste_users(request):
    
    listeusers = Users.objects.all()  # Ajustez selon votre modèle
    messages.get_messages(request)  # Récupérer les messages pour affichage
    return render(request, 'Login/liste_user.html', {'listeusers': listeusers})


def supprimer_utilisateur(request, id_utilisateur):  # Renomme le paramètre pour la cohérence

    
    try:
        user = Users.objects.get(id=id_utilisateur)  # Utilise le bon paramètre ici
        user.delete()
        messages.success(request, "Utilisateur supprimé avec succès.")
    except Users.DoesNotExist:
        messages.error(request, "Utilisateur introuvable!")

    return redirect('liste_users')  # Redirige vers la vue de liste



def continuer(request):
    # Ici, vous pouvez vérifier si l'utilisateur est connecté avant de rendre la page
    if 'user_id' in request.session:
        return render(request, 'index.html', {'is_logged_in': is_logged_in})  # Assurez-vous que ce template existe
    else:
        messages.error(request, "Vous devez être connecté pour accéder à cette page.")
        return redirect('connect')  # Redirige vers la page de connexion

# Create your views here.



def disconnect(request):
    # Supprimer l'utilisateur de la session
    if 'user_id' in request.session:
        del request.session['user_id']
        messages.success(request, "Déconnexion réussie.")
    
    # Vérifiez si l'utilisateur est connecté (après déconnexion, cela sera False)
    is_logged_in = 'user_id' in request.session
    return render(request, 'login/index.html', {'is_logged_in': is_logged_in})