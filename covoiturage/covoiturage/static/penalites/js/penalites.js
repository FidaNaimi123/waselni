document.addEventListener('DOMContentLoaded', function() {
    // Initialiser toutes les jauges
    initializeGauges();
    
    // Fonction pour initialiser les jauges
    function initializeGauges() {
        document.querySelectorAll('.score-gauge').forEach(gauge => {
            const score = parseInt(gauge.dataset.score);
            gauge.style.setProperty('--score-height', `${score}%`);
            
            // Définir la couleur en fonction du score
            let color;
            if (score >= 80) {
                color = '#00C851';  // Vert pour bon score
            } else if (score >= 50) {
                color = '#ffbb33';  // Orange pour score moyen
            } else {
                color = '#ff4444';  // Rouge pour mauvais score
            }
            
            gauge.style.setProperty('--score-color', color);
        });
    }
});

// Fonction pour modifier le score (pour les admins)
function modifierScore(userId) {
    const newScore = prompt('Entrez le nouveau score (0-100):');
    if (newScore !== null && !isNaN(newScore) && newScore >= 0 && newScore <= 100) {
        // Envoyer au serveur via fetch
        fetch('/api/modifier-score/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                user_id: userId,
                score: parseInt(newScore)
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Erreur lors de la modification du score');
            }
        });
    }
}

// Fonction utilitaire pour obtenir le token CSRF
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