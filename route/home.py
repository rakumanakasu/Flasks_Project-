from flask import Blueprint, render_template
from helper import product_db

home_bp = Blueprint("home", __name__)


@home_bp.route('/')
@home_bp.route('/home')
def home():
    products = []
    carousel_images = []
    error = ''

    try:
        # fetch products from SQLite
        products = product_db.get_products_from_db()

        # Make sure rating fields exist
        for p in products:
            p.setdefault('rating_rate', 0)
            p.setdefault('rating_count', 0)

        # Get first 3 images for carousel
        carousel_images = [('/photos/' + p['image']) if p['image'] else '/static/default.jpg'
                           for p in products[:3]]
    except Exception as e:
        error = str(e)

    return render_template('home.html', products=products, carousel_images=carousel_images, error=error)
