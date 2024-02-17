
    // Toggle the visibility of the jokes container when the button is clicked
    document.getElementById('show-jokes-btn').addEventListener('click', function() {
        var jokesContainer = document.getElementById('jokes-container');
        jokesContainer.style.display = jokesContainer.style.display === 'none' ? 'block' : 'none';
    });