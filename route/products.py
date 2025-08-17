import sqlite3
from flask import Blueprint, render_template
from config import DB_PATH

product_bp = Blueprint('product', __name__)

# ----------------------------
# Database connection
# ----------------------------
def get_products_from_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ----------------------------
# Routes
# ----------------------------
@product_bp.route('/products')
def products():
    products = []
    error = ''
    try:
        products = get_products_from_db()
    except Exception as e:
        error = str(e)
    return render_template('product.html', products=products, error=error)
