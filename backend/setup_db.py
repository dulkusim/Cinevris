import csv
import sqlite3

# Connect to the database
conn = sqlite3.connect('movielens.db')
cursor = conn.cursor()

# Enable Foreign Keys
cursor.execute("PRAGMA foreign_keys=ON;")

# Create Tables
print('Creating movies table')
cursor.execute('''
               CREATE TABLE IF NOT EXISTS movies(
                   movieId INTEGER PRIMARY KEY,
                   title TEXT,
                   genres TEXT,
                   UNIQUE(title, genres)
                )
''')

print('Creating ratings table')
cursor.execute('''
               CREATE TABLE IF NOT EXISTS ratings(
                   userId INTEGER,
                   movieId INTEGER,
                   rating REAL,
                   timestamp INTEGER,
                   PRIMARY KEY (userId, movieId),
                   FOREIGN KEY(movieId) REFERENCES movies(movieId)
               )
''')

print('Creating tags table')
cursor.execute('''
               CREATE TABLE IF NOT EXISTS tags(
                   userId INTEGER,
                   movieId INTEGER,
                   tag TEXT,
                   timestamp INTEGER,
                   FOREIGN KEY(movieId) REFERENCES movies(movieId)
                )
''')

print('Populating Movies')
with open('./data/movies.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)
    
    for row in reader:
        cursor.execute('''
                       INSERT OR IGNORE INTO movies(movieId, title, genres)
                       VALUES (?,?,?)
                       ''',(row[0],row[1],row[2]))

print('Populating Ratings')
with open('./data/ratings.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)
    
    for row in reader:
        cursor.execute('''
                       INSERT OR IGNORE INTO ratings(userId, movieId, rating, timestamp)
                       VALUES (?,?,?,?)
                       ''',(row[0],row[1],row[2],row[3]))

print('Populating Tags')
with open('./data/tags.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)
    
    for row in reader:
        cursor.execute('''
                       INSERT INTO tags(userId, movieId, tag, timestamp)
                       VALUES (?,?,?,?)
                       ''',(row[0],row[1],row[2],row[3]))

conn.commit()
conn.close()
print('All Setups Completed')