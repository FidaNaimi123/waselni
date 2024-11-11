from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from .models import Evaluation, Trajet
from .forms import EvaluationForm
from django.utils import timezone
from datetime import timedelta

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
            evaluation.evaluateur.email = request.user.email

            # Ensure `evale` is set, for example:
            # Assuming `evale` is a field representing the driver or another user
            evaluation.evale = trajet.conducteur_nom_complet  # Replace with the correct field for the user being evaluated

            # Check date constraints
            if trajet.date_depart < timezone.now().date():
                form.add_error(None, "Vous ne pouvez pas évaluer un trajet déjà passé.")
                return render(request, 'evaluation/evaluation_form.html', {'form': form})

            evaluation.save()
            return redirect('trajets_disponibles', trajet_id=trajet.id)
    else:
        form = EvaluationForm()

    return render(request, 'evaluation/evaluation_form.html', {'form': form})


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
