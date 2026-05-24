from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import get_connection
from pydantic import BaseModel

app = FastAPI()

# CORS: allows the frontend to call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # allow requests from any origin
    allow_methods=["*"],    # allow GET, POST, etc.
    allow_headers=["*"],
)

# Search movies: GET /movies?search={keyword}
@app.get("/movielens/api/movies")
def search_movies(search: str = ""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM movies WHERE title LIKE ?",
        (f"%{search}%",)
    )

    movies = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {"status": "success", "movies": movies}


# Get Ratings for a Movie: GET /ratings/{movieId}
@app.get('/movielens/api/ratings/{movieId}')
def get_ratings(movieId : int):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM ratings WHERE movieId = ?",
        (movieId,)
    )
    
    ratings = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {"status": "success", "ratings": ratings}


# Add a New Movie: POST /movies
class NewMovie(BaseModel):
    title : str
    genres: str
    
@app.post('/movielens/api/movies')
def add_movie(movie: NewMovie):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO movies(title, genres) VALUES (?,?)",
        (movie.title, movie.genres)
    )

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return {"status": "success", "movieId": new_id}