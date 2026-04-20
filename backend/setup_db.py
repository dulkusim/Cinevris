import csv
import sqlite3

conn = sqlite3.connect('movielens.db')

cursor = conn.cursor()

print('Creating table')
cursor.execute('''
               CREATE TABLE IF NOT EXISTS movies(
                   movieId INTEGER PRIMARY KEY,
                   title TEXT,
                   genres TEXT
                )
''')

print('Setup beginning')
with open('./data/movies.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)
    
    for row in reader:
        cursor.execute('''
                       INSERT OR IGNORE INTO movies(movieId, title, genres)
                       VALUES (?,?,?)
                       ''',(row[0],row[1],row[2]))

conn.commit()
conn.close()
print('Setup Completed')