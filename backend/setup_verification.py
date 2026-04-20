import sqlite3

conn = sqlite3.connect('movielens.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM movies')
rows = cursor.fetchall()

print(f"Total movies: {len(rows)}")

print("First 5 movies:")
for row in rows[:5]:
    print(row)

conn.close()