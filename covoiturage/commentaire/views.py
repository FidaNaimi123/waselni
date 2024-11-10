from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from .models import Commentaire
from .forms import CommentaireForm
from evaluation.models import Evaluation

@login_required
def create_commentaire(request, evaluation_id):
    
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)

    
    if evaluation.evaluateur != request.user:
        raise PermissionDenied("Vous ne pouvez commenter que vos propres évaluations.")
    
    if request.method == 'POST':
        form = CommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.evaluation = evaluation
            commentaire.save()
            return redirect('evaluation_detail', evaluation_id=evaluation.id)
    else:
        form = CommentaireForm()

    return render(request, 'commentaire_form.html', {'form': form, 'evaluation': evaluation})

@login_required
def edit_commentaire(request, commentaire_id):
    
    commentaire = get_object_or_404(Commentaire, id=commentaire_id)


    if commentaire.evaluation.evaluateur != request.user:
        raise PermissionDenied("Vous ne pouvez modifier que vos propres commentaires.")

    if request.method == 'POST':
        form = CommentaireForm(request.POST, instance=commentaire)
        if form.is_valid():
            form.save()
            return redirect('evaluation_detail', evaluation_id=commentaire.evaluation.id)
    else:
        form = CommentaireForm(instance=commentaire)

    return render(request, 'commentaire_form.html', {'form': form, 'commentaire': commentaire})

@login_required
def delete_commentaire(request, commentaire_id):
    
    commentaire = get_object_or_404(Commentaire, id=commentaire_id)

    
    if commentaire.evaluation.evaluateur != request.user:
        raise PermissionDenied("Vous ne pouvez supprimer que vos propres commentaires.")

    if request.method == 'POST':
        commentaire.delete()
        return redirect('evaluation_detail', evaluation_id=commentaire.evaluation.id)

    return render(request, 'confirm_delete_commentaire.html', {'commentaire': commentaire})
