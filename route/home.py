from flask import Blueprint, render_template, request
import requests

home_bp = Blueprint("home", __name__)

@home_bp.route('/')
@home_bp.route('/home')
def home():
    products = []
    carousel_images = []
    error = ''
    try:
        r = requests.get('https://fakestoreapi.com/products')
        if r.status_code == 200:
            products = r.json()
            carousel_images = [product['image'] for product in products[:3]]
    except Exception as e:
        error = e
    return render_template('home.html', products=products, error=error, carousel_images=carousel_images)
