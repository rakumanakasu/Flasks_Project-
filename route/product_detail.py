from flask import Blueprint, render_template, request
import requests

product_detail_bp = Blueprint("product_detail", __name__)

@product_detail_bp.route('/product')
def product_detail():
    product_id = request.args.get('product_id', type=int)
    if not product_id:
        return "Missing product_id", 400
    try:
        r = requests.get(f'https://fakestoreapi.com/products/{product_id}')
        if r.status_code == 200:
            product = r.json()
            return render_template('productdetail.html', product=product)
        return 'Product not found', 404
    except Exception as e:
        return str(e), 500
