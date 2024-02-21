
    // Toggle the visibility of the jokes container when the button is clicked
    document.getElementById('show-jokes-btn').addEventListener('click', function() {
        var jokesContainer = document.getElementById('jokes-container');
        jokesContainer.style.display = jokesContainer.style.display === 'none' ? 'block' : 'none';
    });

async function fetchLastJoke() {
    try {
        const response = await fetch('/last_joke');
        if (!response.ok) {
            throw new Error('Failed to fetch last joke');
        }
        const data = await response.json();
        
        // Extract the joke text
        const jokeText = data.joke;
        
       return jokeText
    } catch (error) {
        console.error('Error fetching last joke:', error);
        return null;
    }
}
    
async function shareOnTwitter() {
    const jokeText = await fetchLastJoke();
    if (jokeText !== null) {
        const appUrl = "https://your-chuck-norris-app.com";
        const shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(jokeText)}`;
        window.open(shareUrl, "_blank");
    } else {
        console.error('No joke available');
    }
}