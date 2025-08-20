import sqlite3

conn = sqlite3.connect('site.db')
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    image TEXT,
    category TEXT,
    rating_rate REAL DEFAULT 0,   
    rating_count INTEGER DEFAULT 0  
)
''')

conn.commit()
conn.close()

print("Table updated with rating!")
