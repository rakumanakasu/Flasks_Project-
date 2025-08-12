from flask import Blueprint, render_template
import requests

product_bp = Blueprint("product", __name__)

@product_bp.route('/product')
def products():
    products = []
    carousel_images = []
    error = ''
    try:
        r = requests.get('https://fakestoreapi.com/products')
        if r.status_code == 200:
            products = r.json()
            carousel_images = [product['image'] for product in products[:3]]
        else:
            error = f"API returned status code {r.status_code}"
    except Exception as e:
        error = str(e)

    return render_template(
        'product.html',
        products=products,
        error=error,
        carousel_images=carousel_images
    )
