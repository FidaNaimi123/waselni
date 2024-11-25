from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from .models import Evaluation
from Trip.models import Trajet
from users.models import Users
from .forms import EvaluationForm
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render

@login_required
def select_trip1(request):
    if request.method == 'POST':
        selected_trajet_id = request.POST.get('selected_trip1')  # Récupérer l'ID du trajet sélectionné
        return redirect('create_evaluation', trajet_id=selected_trajet_id)  # Redirigez vers la vue de création de réservation
    return redirect('home1')
def create_evaluation(request, trajet_id):
    trajet = get_object_or_404(Trajet, id=trajet_id)

    if request.method == 'POST':
        form = EvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.trajet = trajet
            evaluation.evaluateur = request.user  # Associe l'utilisateur connecté comme évaluateur

            # Récupérer l'utilisateur à évaluer (exemple : conducteur)
            # Remplacez 'trajet.conducteur_user_id' par le champ qui correspond à l'ID ou à la clé étrangère vers le modèle `Users`
            evaluation.evale = get_object_or_404(Users, id=trajet.id)

            
    else:
        form = EvaluationForm()

    return render(request, 'evaluation/evaluation_form.html', {'form': form})



def confirmation_view(request):
    # Logique supplémentaire si nécessaire
    return render(request, 'evaluation/confirmation.html')  # Afficher un template

@login_required
def update_evaluation(request, evaluation_id):
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)

    if request.user != evaluation.evaluateur:
        return HttpResponseForbidden("Vous n'avez pas la permission de modifier cette évaluation.")

    if request.method == 'POST':
        form = EvaluationForm(request.POST, instance=evaluation)
        if form.is_valid():
            evaluation = form.save(commit=False)
            
            # Check for self-evaluation again if necessary
            if evaluation.evaluateur == evaluation.evale:
                form.add_error(None, "Vous ne pouvez pas évaluer vous-même.")
                return render(request, 'evaluation/evaluation_form.html', {'form': form})

            evaluation.save()
            return redirect('trajets_disponibles', evaluation_id=evaluation.id)
    else:
        form = EvaluationForm(instance=evaluation)

    return render(request, 'evaluation/evaluation_form.html', {'form': form})

@login_required
def delete_evaluation(request, evaluation_id):
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)


    if request.user != evaluation.evaluateur:
        raise PermissionDenied("Vous n'avez pas la permission de supprimer cette évaluation.")

    if request.method == 'POST':
        evaluation.delete()
        return redirect('trajets_disponibles')

    return render(request, 'evaluation/confirm_delete_evaluation.html', {'evaluation': evaluation})
