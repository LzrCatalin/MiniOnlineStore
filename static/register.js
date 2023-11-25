// script.js
document.addEventListener('DOMContentLoaded', function () {
    // Check if there is an error message after the form submission and show an alert
    var errorMessage = "{{ error_message }}";
    if (errorMessage) {
        alert(errorMessage);
    }
});
