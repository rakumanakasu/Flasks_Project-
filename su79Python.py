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
    category TEXT
)
''')

conn.commit()
conn.close()

print("Table created!")
