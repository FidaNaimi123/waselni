from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from .models import Reclamation
from Trip.models import Trajet
from .forms import ReclamationForm
from django.utils import timezone

class ReclamationCreateView(LoginRequiredMixin, CreateView):
    model = Reclamation
    form_class = ReclamationForm
    template_name = 'reclammation/reclammation_form.html'

    def form_valid(self, form):
        # Fetch the `Trajet` instance related to the reclamation
        trajet = get_object_or_404(Trajet, id=self.kwargs['trajet_id'])

        # Ensure that a reclamation cannot be created for past trips
        if trajet.date_depart < timezone.now().date():
            form.add_error(None, "Vous ne pouvez pas faire une réclamation pour un trajet déjà terminé.")
            return self.form_invalid(form)

        # Associate the logged-in user and the selected trajet with the reclamation
        form.instance.utilisateur = self.request.user
        form.instance.trajet = trajet
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the detail page of the related `Trajet`
        return reverse_lazy('trajet_detail', kwargs={'trajet_id': self.kwargs['trajet_id']})


class ReclamationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Reclamation
    form_class = ReclamationForm
    template_name = 'reclammation/reclammation_form.html'

    def test_func(self):
        reclamation = self.get_object()
        return reclamation.utilisateur == self.request.user

    def get_success_url(self):
        return reverse_lazy('reclamation_detail', kwargs={'reclamation_id': self.object.id})


class ReclamationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Reclamation
    template_name = 'reclammation/confirm_delete_reclamation.html'
    success_url = reverse_lazy('trajet_list')

    def test_func(self):
        reclamation = self.get_object()
        return reclamation.utilisateur == self.request.user
