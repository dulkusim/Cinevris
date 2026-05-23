from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import get_connection

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