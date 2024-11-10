from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from .models import Evaluation, Trajet
from .forms import EvaluationForm
from django.utils import timezone
from datetime import timedelta

@login_required
def create_evaluation(request, trajet_id):
    trajet = get_object_or_404(Trajet, id=trajet_id)

    if request.method == 'POST':
        form = EvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.trajet = trajet
            evaluation.evaluateur = request.user

            # Check that the evaluateur is not evaluating themselves
            if evaluation.evaluateur == evaluation.evale:
                form.add_error(None, "Vous ne pouvez pas évaluer vous-même.")
                return render(request, 'evaluation_form.html', {'form': form})

            # Check date constraints
            if evaluation.date_evaluation > (trajet.date_fin + timedelta(days=30)):
                form.add_error(None, "L'évaluation doit avoir lieu dans les 30 jours suivant la fin du trajet.")
                return render(request, 'evaluation_form.html', {'form': form})

            evaluation.save()
            return redirect('trajet_detail', trajet_id=trajet.id)
    else:
        form = EvaluationForm()

    return render(request, 'evaluation_form.html', {'form': form})

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
                return render(request, 'evaluation_form.html', {'form': form})

            evaluation.save()
            return redirect('evaluation_detail', evaluation_id=evaluation.id)
    else:
        form = EvaluationForm(instance=evaluation)

    return render(request, 'evaluation_form.html', {'form': form})

@login_required
def delete_evaluation(request, evaluation_id):
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)


    if request.user != evaluation.evaluateur:
        raise PermissionDenied("Vous n'avez pas la permission de supprimer cette évaluation.")

    if request.method == 'POST':
        evaluation.delete()
        return redirect('trajet_list')

    return render(request, 'confirm_delete_evaluation.html', {'evaluation': evaluation})
