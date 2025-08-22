from flask import Blueprint, render_template
import requests

home_bp = Blueprint("home", __name__)

@home_bp.route('/')
@home_bp.route('/home')
def home():
    products = []
    error = ''

    # Fetch products from your API
    try:
        resp = requests.get("https://admindashboardflask-production-1a1e.up.railway.app/api/products")
        if resp.status_code == 200:
            products = resp.json()
        else:
            error = f"API error {resp.status_code}"
    except Exception as e:
        error = f"Could not fetch products: {str(e)}"

    # Ensure each product has rating fields
    for p in products:
        p.setdefault('rating_rate', 0)
        p.setdefault('rating_count', 0)

    # Ensure each product has a valid image URL
    for p in products:
        if not p.get('image') or p['image'].strip() == '':
            p['image'] = '/static/default.jpg'  # fallback local image

    # Prepare carousel images (first 3 products)
    carousel_images = [p['image'] for p in products[:3]]

    return render_template(
        'home.html',
        products=products,
        carousel_images=carousel_images,
        error=error
    )
