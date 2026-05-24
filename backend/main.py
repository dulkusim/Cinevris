from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import get_connection
from pydantic import BaseModel
from scipy.stats import pearsonr
import math

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


# Get Recommendations: POST /recommendations
class RatingInput(BaseModel):
    movieId: int
    rating: float


class RecommendationRequest(BaseModel):
    ratings: list[RatingInput]


@app.post("/movielens/api/recommendations")
def get_recommendations(request: RecommendationRequest):

    K = 20
    N = 10

    # STEP 1: Build active user ratings dictionary
    user_ratings = {r.movieId: r.rating for r in request.ratings}

    if len(user_ratings) < 2:
        return {"status": "success", "recommendations": []}

    conn = get_connection()
    cursor = conn.cursor()

    # STEP 2: Find users who rated the same movies
    placeholders = ",".join("?" * len(user_ratings))

    cursor.execute(
        f"""
        SELECT userId, movieId, rating
        FROM ratings
        WHERE movieId IN ({placeholders})
        """, list(user_ratings.keys())
    )

    # STEP 3: Group ratings by user
    neighbor_ratings = {}

    for row in cursor.fetchall():
        uid = row["userId"]
        mid = row["movieId"]
        rat = row["rating"]

        if uid not in neighbor_ratings:
            neighbor_ratings[uid] = {}

        neighbor_ratings[uid][mid] = rat

    # STEP 4: Compute Pearson similarity
    similarities = {}

    for uid, their_ratings in neighbor_ratings.items():
        common = [
            mid for mid in user_ratings
            if mid in their_ratings
        ]

        # Need at least 2 common movies
        if len(common) < 2:
            continue

        u_vec = [user_ratings[mid] for mid in common]
        v_vec = [their_ratings[mid] for mid in common]

        # Prevent Pearson NaN
        if len(set(u_vec)) == 1 or len(set(v_vec)) == 1:
            continue

        corr, _ = pearsonr(u_vec, v_vec)

        if math.isnan(corr) or corr <= 0:
            continue

        similarities[uid] = corr

    # STEP 5: Select Top-K similar users

    top_k = sorted(similarities, key=similarities.get, reverse=True)[:K]

    if len(top_k) == 0:
        conn.close()
        return {"status": "success", "recommendations": []}

    # STEP 6: Fetch ALL ratings from top-K users
    placeholders = ",".join("?" * len(top_k))

    cursor.execute(
        f"""
        SELECT userId, movieId, rating
        FROM ratings
        WHERE userId IN ({placeholders})
        """, top_k
    )

    full_neighbor_ratings = {}

    for row in cursor.fetchall():

        uid = row["userId"]
        mid = row["movieId"]
        rat = row["rating"]

        if uid not in full_neighbor_ratings:
            full_neighbor_ratings[uid] = {}

        full_neighbor_ratings[uid][mid] = rat

    # STEP 7: Predict ratings for unseen movies

    u_mean = sum(user_ratings.values()) / len(user_ratings)

    predictions = {}

    for uid in top_k:
        sim = similarities[uid]
        their_ratings = full_neighbor_ratings[uid]
        v_mean = sum(their_ratings.values()) / len(their_ratings)

        for mid, r in their_ratings.items():
            # Skip movies already rated by active user
            if mid in user_ratings:
                continue

            if mid not in predictions:
                predictions[mid] = [0.0, 0.0]

            predictions[mid][0] += sim * (r - v_mean)
            predictions[mid][1] += abs(sim)

    # STEP 8: Compute final predicted ratings
    predicted_ratings = {}

    for mid, (num, den) in predictions.items():
        if den == 0:
            continue
        predicted_ratings[mid] = u_mean + (num / den)

    # STEP 9: Select Top-N recommendations
    top_n = sorted(predicted_ratings, key=predicted_ratings.get, reverse=True)[:N]

    recommendations = []

    for mid in top_n:
        cursor.execute(
            """
            SELECT title, genres
            FROM movies
            WHERE movieId = ?
            """, (mid,)
        )

        movie = cursor.fetchone()

        if movie:
            recommendations.append({
                "movieId": mid,
                "title": movie["title"],
                "genres": movie["genres"],
                "predictedRating": round(predicted_ratings[mid], 2)
            })

    conn.close()

    return {"status": "success", "recommendations": recommendations}