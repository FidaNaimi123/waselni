document.addEventListener('DOMContentLoaded', function() {
    const boutonsSuppression = document.querySelectorAll('.btn-supprimer-commentaire');
    
    boutonsSuppression.forEach(bouton => {
        bouton.addEventListener('click', function(e) {
            const commentaireId = this.dataset.commentaireId;
            
            if (confirm('Êtes-vous sûr de vouloir supprimer ce commentaire ?')) {
                fetch(`/commentaire/supprimer/${commentaireId}/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        document.getElementById(`commentaire-${commentaireId}`).remove();
                    } else {
                        alert(data.message);
                    }
                })
                .catch(error => {
                    console.error('Erreur:', error);
                    alert('Une erreur est survenue lors de la suppression du commentaire');
                });
            }
        });
    });
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});