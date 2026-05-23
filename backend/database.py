import sqlite3

def get_connection():
    conn = sqlite3.connect('./movielens.db')
    conn.row_factory = sqlite3.Row  # rows behave like dict, instead of tuples
    return conn