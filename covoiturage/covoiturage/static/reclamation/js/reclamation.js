document.addEventListener('DOMContentLoaded', function () {
    // Handle form submission confirmation
    const form = document.querySelector('form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Show confirmation modal before submitting
        const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
        modal.show();

        // If user confirms, submit the form
        document.getElementById('confirmSubmit').addEventListener('click', function() {
            form.submit();
        });
    });
});
