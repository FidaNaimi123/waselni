document.addEventListener("DOMContentLoaded", function() {
    const stars = document.querySelectorAll('.star');
    stars.forEach((star, index) => {
        star.addEventListener('click', function() {
            // Marque la note
            const selectedStar = index + 1;
            const input = document.querySelector(`input[value="${selectedStar}"]`);
            if (input) {
                input.checked = true;
            }
        });
    });
});
