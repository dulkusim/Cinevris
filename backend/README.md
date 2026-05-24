# Cinevris Backend

FastAPI backend for the Cinevris movie recommendation system, powered by user-based collaborative filtering (Pearson similarity) over the MovieLens dataset.

## Project Structure

```
backend/
├── main.py               # FastAPI application and all API endpoints
├── database.py           # SQLite connection file
├── setup_db.py           # Creates and populates the SQLite database
├── setup_verification.py # Simple verification the database was populated correctly
├── requirements.txt      # Python dependencies
└── data/
    ├── movies.csv        # MovieLens movie titles and genres
    ├── ratings.csv       # User ratings (userId, movieId, rating, timestamp)
    └── tags.csv          # User tags (userId, movieId, tag, timestamp)
```

## Prerequisites

- Python 3.10 or higher
- pip

## Setup

### 1. Create and activate a virtual environment

**Windows (PowerShell)**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create and populate the database

Run the setup script from inside the `backend/` directory. It reads the CSV files in `data/`, creates `movielens.db`, and inserts all movies, ratings, and tags.

```bash
python setup_db.py
```

Expected output:
```
Creating movies table
Creating ratings table
Creating tags table
Populating Movies
Populating Ratings
Populating Tags
All Setups Completed
```

### 4. (Optional) Verify the database

```bash
python setup_verification.py
```

This prints the total movie count and the first five rows of the `movies` table.

## Running the Server

Start the development server from inside the `backend/` directory:

```bash
uvicorn main:app --reload --port 3000 
```

The API will be available at `http://127.0.0.1:3000`.

Interactive docs (Swagger UI): `http://127.0.0.1:3000/docs`

## API Reference

All endpoints are prefixed with `/movielens/api`.

### Search Movies

```
GET /movielens/api/movies?search={keyword}
```

Returns movies whose title contains the search keyword. An empty `search` value returns all movies.

**Example**
```
GET /movielens/api/movies?search=toy
```

---

### Add a Movie

```
POST /movielens/api/movies
Content-Type: application/json
```

**Request body**
```json
{ "title": "My Movie (2024)", "genres": "Drama|Thriller" }
```

Duplicate `(title, genres)` pairs are silently ignored.

**Response**
```json
{ "status": "success", "movieId": 9743 }
```

---

### Get Ratings for a Movie

```
GET /movielens/api/ratings/{movieId}
```

**Example**
```
GET /movielens/api/ratings/1
```
```json
{
  "status": "success",
  "ratings": [
    { "userId": 7, "movieId": 1, "rating": 3.0, "timestamp": 851866703 }
  ]
}
```

---

### Get Recommendations

```
POST /movielens/api/recommendations
Content-Type: application/json
```

Accepts a list of the active user's movie ratings and returns up to 10 predicted recommendations using user-based collaborative filtering (Pearson similarity, top-20 neighbours).

At least **2 rated movies** are required; fewer returns an empty list.

**Request body**
```json
{
  "ratings": [
    { "movieId": 1,  "rating": 5.0 },
    { "movieId": 32, "rating": 4.0 }
  ]
}
```

**Response**
```json
{
  "status": "success",
  "recommendations": [
    {
      "movieId": 296,
      "title": "Pulp Fiction (1994)",
      "genres": "Comedy|Crime|Drama|Thriller",
      "predictedRating": 4.37
    }
  ]
}
```

## Database Schema

```sql
CREATE TABLE movies (
    movieId  INTEGER PRIMARY KEY,
    title    TEXT,
    genres   TEXT,
    UNIQUE(title, genres)
);

CREATE TABLE ratings (
    userId    INTEGER,
    movieId   INTEGER,
    rating    REAL,
    timestamp INTEGER,
    PRIMARY KEY (userId, movieId),
    FOREIGN KEY (movieId) REFERENCES movies(movieId)
);

CREATE TABLE tags (
    userId    INTEGER,
    movieId   INTEGER,
    tag       TEXT,
    timestamp INTEGER,
    FOREIGN KEY (movieId) REFERENCES movies(movieId)
);
```

## Dependencies

| Package  | Purpose                                   |
|----------|-------------------------------------------|
| fastapi  | Web framework and request/response models |
| uvicorn  | ASGI server                               |
| scipy    | Pearson correlation for similarity scores |
