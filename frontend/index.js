const BASE_URL = 'http://127.0.0.1:3000/movielens/api'

// In-memory ratings store: { movieId: rating }
const myRatings = {}

// ── Wire up buttons when page loads ──────────────────────
document.getElementById('add-movie-btn').addEventListener('click', addMovie)
document.getElementById('search-btn').addEventListener('click', searchMovies)
document.getElementById('recommend-btn').addEventListener('click', getRecommendations)


// ── FEATURE 1: Add a Movie ────────────────────────────────
async function addMovie() {
    const title  = document.getElementById('new-title').value.trim()
    const genres = document.getElementById('new-genres').value.trim()
    const feedback = document.getElementById('add-movie-feedback')

    // Validate inputs before calling backend
    if (!title || !genres) {
        feedback.textContent = 'Please fill in both title and genres.'
        feedback.style.color = 'red'
        return
    }

    const response = await fetch(`${BASE_URL}/movies`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, genres })
    })

    const data = await response.json()

    if (response.ok) {
        feedback.textContent = `Movie added successfully! ID: ${data.movieId}`
        feedback.style.color = 'green'
    } else {
        feedback.textContent = `Error: ${data.detail}`
        feedback.style.color = 'red'
    }
}


// ── FEATURE 2: Search Movies ──────────────────────────────
async function searchMovies() {
    const keyword = document.getElementById('search-input').value.trim()
    const container = document.getElementById('search-results')

    const response = await fetch(`${BASE_URL}/movies?search=${encodeURIComponent(keyword)}`)
    const data = await response.json()

    if (data.movies.length === 0) {
        container.innerHTML = '<p>No movies found.</p>'
        return
    }

    // Build a table of results
    let html = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Genres</th>
                    <th>Avg Rating</th>
                    <th>Your Rating</th>
                </tr>
            </thead>
            <tbody>
    `

    for (const movie of data.movies) {
        const avg = await getAverageRating(movie.movieId)
        html += `
            <tr>
                <td>${movie.movieId}</td>
                <td>${movie.title}</td>
                <td>${movie.genres}</td>
                <td>${avg}</td>
                <td>
                    <input type="number" min="0.5" max="5" step="0.5"
                           id="rate-${movie.movieId}"
                           placeholder="0.5–5">
                    <button onclick="rateMovie(${movie.movieId})">Rate</button>
                </td>
            </tr>
        `
    }

    html += '</tbody></table>'
    container.innerHTML = html
}


// ── HELPER: Get average rating for a movie ────────────────
async function getAverageRating(movieId) {
    const response = await fetch(`${BASE_URL}/ratings/${movieId}`)
    const data = await response.json()

    if (data.ratings.length === 0) return 'No ratings yet'

    const sum = data.ratings.reduce((acc, r) => acc + r.rating, 0)
    const avg = sum / data.ratings.length
    return avg.toFixed(2)
}


// ── FEATURE 3: Rate a Movie (in memory only) ──────────────
function rateMovie(movieId) {
    const input = document.getElementById(`rate-${movieId}`)
    const value = parseFloat(input.value)

    if (isNaN(value) || value < 0.5 || value > 5) {
        alert('Please enter a rating between 0.5 and 5.')
        return
    }

    myRatings[movieId] = value
    alert(`Rated movie ${movieId}: ${value} stars. Saved for recommendations.`)
}


// ── FEATURE 4: Get Recommendations ───────────────────────
async function getRecommendations() {
    const container = document.getElementById('recommendations-results')

    if (Object.keys(myRatings).length === 0) {
        container.innerHTML = '<p>Please rate at least one movie first.</p>'
        return
    }

    // Convert myRatings dict to the array format the backend expects
    const ratingsArray = Object.entries(myRatings).map(([movieId, rating]) => ({
        movieId: parseInt(movieId),
        rating: rating
    }))

    const response = await fetch(`${BASE_URL}/recommendations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ratings: ratingsArray })
    })

    const data = await response.json()

    if (data.recommendations.length === 0) {
        container.innerHTML = '<p>No recommendations found. Try rating more movies.</p>'
        return
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Genres</th>
                    <th>Predicted Rating</th>
                </tr>
            </thead>
            <tbody>
    `

    for (const movie of data.recommendations) {
        html += `
            <tr>
                <td>${movie.movieId}</td>
                <td>${movie.title}</td>
                <td>${movie.genres}</td>
                <td>${movie.predictedRating}</td>
            </tr>
        `
    }

    html += '</tbody></table>'
    container.innerHTML = html
}