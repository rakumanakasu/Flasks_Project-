from flask import Blueprint, render_template
import requests

detail_bp = Blueprint("detail", __name__)

@detail_bp.route('/detail/<int:pro_id>')
def detail(pro_id):
    product = None
    error = ''
    try:
        r = requests.get(f"https://fakestoreapi.com/products/{pro_id}")
        if r.status_code == 200:
            product = r.json()
        else:
            error = f"Product with ID {pro_id} not found."
    except Exception as e:
        error = str(e)
    return render_template('detail.html', product=product, error=error)
