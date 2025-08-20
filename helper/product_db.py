import sqlite3
from config import DB_PATH

def get_products_from_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]
