from flask import Blueprint, render_template
from helper import product_db
import requests

home_bp = Blueprint("home", __name__)



@home_bp.route('/')
@home_bp.route('/home')
def home():
    products = []
    error = ''
    try:
        resp = requests.get("https://admindashboardflask-production-1a1e.up.railway.app/api/products")
        if resp.status_code == 200:
            products = resp.json()
        else:
            error = f"API error {resp.status_code}"
    except Exception as e:
        error = str(e)

    for p in products:
        p.setdefault('rating_rate', 0)
        p.setdefault('rating_count', 0)

    carousel_images = [('/photos/' + p['image']) if p['image'] else '/static/default.jpg'
                       for p in products[:3]]

    return render_template('home.html', products=products, carousel_images=carousel_images, error=error)
