const trendsChart = new Chart(
    document.getElementById('trendsChart').getContext('2d'),
    {
        type: 'line',
        data: {
            labels: Array.from(document.querySelectorAll('[data-month]')).map(el => el.dataset.month),
            datasets: [{
                label: 'Nombre de pénalités',
                data: Array.from(document.querySelectorAll('[data-total]')).map(el => el.dataset.total),
                borderColor: '#4a90e2',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    }
);

// Gestion des filtres
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        // Ajoutez ici la logique de filtrage
    });
});