# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Penalite
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Penalite

def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    penalites = Penalite.objects.all().order_by('-date_penalite')
    return render(request, 'penalites/admin_dashboard.html', {
        'penalites': penalites
    })

@login_required
@user_passes_test(is_admin)
def ajouter_penalite(request):
    if request.method == 'POST':
        utilisateur_id = request.POST.get('utilisateur')
        type_penalite = request.POST.get('type_penalite')
        description = request.POST.get('description')
        duree_restriction = int(request.POST.get('duree_restriction', 0))
        
        penalite = Penalite.objects.create(
            utilisateur_id=utilisateur_id,
            type_penalite=type_penalite,
            description=description
        )
        
        if duree_restriction > 0:
            utilisateur = penalite.utilisateur
            utilisateur.date_fin_restriction = timezone.now() + timedelta(days=duree_restriction)
            utilisateur.save()
            
        messages.success(request, 'Pénalité ajoutée avec succès')
        return redirect('admin_dashboard')
        
    return render(request, 'penalites/ajouter_penalite.html')

@login_required
def profil_utilisateur(request):
    penalites = Penalite.objects.filter(utilisateur=request.user).order_by('-date_penalite')
    score = calculer_score(request.user)
    return render(request, 'penalites/profil_utilisateur.html', {
        'penalites': penalites,
        'score': score
    })

def calculer_score(utilisateur):
    # Score initial de 100
    score = 100
    penalites = Penalite.objects.filter(utilisateur=utilisateur)
    
    for penalite in penalites:
        if penalite.type_penalite == 'annulation_tardive':
            score -= 5
        elif penalite.type_penalite == 'harcelement':
            score -= 20
        elif penalite.type_penalite == 'point_descente_faux':
            score -= 3
        # Ajouter d'autres conditions selon les types de pénalités
        
    return max(0, score)  # Le score ne peut pas être négatif




@login_required
def dashboard_view(request):
    # Récupérer toutes les pénalités de l'utilisateur
    penalites = Penalite.objects.filter(utilisateur=request.user).order_by('-date_penalite')
    
    # Calculer les statistiques
    total_penalites = penalites.count()
    penalites_recentes = penalites.filter(
        date_penalite__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Calculer les statistiques par type
    stats_par_type = penalites.values('type_penalite').annotate(
        total=Count('id')
    )
    
    # Calculer les tendances mensuelles
    mois_derniers = penalites.filter(
        date_penalite__gte=timezone.now() - timedelta(days=180)
    ).values('date_penalite__month').annotate(
        total=Count('id')
    ).order_by('date_penalite__month')

    context = {
        'penalites': penalites,
        'total_penalites': total_penalites,
        'penalites_recentes': penalites_recentes,
        'stats_par_type': stats_par_type,
        'mois_derniers': mois_derniers,
        'statut_compte': "En règle" if not penalites.filter(supprimer_compte=True).exists() else "Attention",
    }
    
    return render(request, 'penalites/dashboard.html', context)

@login_required
def historique(request):
    penalites = Penalite.objects.filter(utilisateur=request.user).order_by('-date_penalite')
    return render(request, 'penalites/historique.html', {'penalites': penalites})