from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import json
import requests
from datetime import date
from dotenv import load_dotenv
import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from invoice import send_pdf_to_telegram




app = Flask(__name__)

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

app.secret_key = os.getenv("SECRET_KEY")

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("EMAIL_USER")
app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASS")
app.config['MAIL_DEFAULT_SENDER'] = ('good day', app.config['MAIL_USERNAME'])




mail = Mail(app)
@app.get('/')
@app.get('/home')
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

@app.get('/detail/<int:pro_id>')
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




# @app.get('/about')
# def about():
#     return render_template('about.html')

# @app.get('/about')
# def about():
#     return render_template('about.html')

@app.route('/products')
def products():
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
    return render_template('product.html', products=products, error=error,carousel_images=carousel_images)

# @app.route('/product/<int:product_id>')
# def product_detail(product_id):
#     try:
#         r = requests.get(f'https://fakestoreapi.com/products/{product_id}')
#         if r.status_code == 200:
#             product = r.json()
#             return render_template('productdetail.html', product=product)
#         return 'Product not found', 404
#     except Exception as e:
#         return str(e), 500
@app.get('/cart')
def cart():
    return render_template('cart.html')


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')

        cart_json = request.form.get('cart_data')
        try:
            cart_list = json.loads(cart_json) if cart_json else []
        except json.JSONDecodeError:
            cart_list = []

        total = sum(item.get('qty', 0) * item.get('price', 0) for item in cart_list)

        # Email invoice
        invoice_html = render_template('invoice_email.html',
                                       name=name,
                                       phone=phone,
                                       email=email,
                                       address=address,
                                       cart_list=cart_list,
                                       total=total)

        msg = Message(subject='Your Order Invoice',
                      recipients=[email],
                      html=invoice_html)

        try:
            mail.send(msg)

            # 🔹 1. Send invoice text to Telegram
            message_lines = [
                f"<strong>🧾 Invoice #{date.today().strftime('%Y%m%d')}</strong>",
                f"<code>👤 {name}</code>",
                f"<code>📧 {email}</code>",
                f"<code>📆 {date.today()}</code>",
                f"<code>🏠 {address}</code>",
                "<code>=======================</code>",
            ]
            for i, item in enumerate(cart_list, start=1):
                message_lines.append(
                    f"<code>{i}. {item['title']} x{item['qty']} = ${item['price']}</code>"
                )
            message_lines.append("<code>=======================</code>")
            message_lines.append(f"<code>💵 Total: ${total:.2f}</code>")

            telegram_message = "\n".join(message_lines)
            requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                data={"chat_id": chat_id, "text": telegram_message, "parse_mode": "HTML"}
            )

            # 🔹 2. Generate PDF invoice
            buffer = io.BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=letter)
            pdf.drawString(50, 750, f"Invoice for {name}")
            pdf.drawString(50, 735, f"Email: {email}")
            pdf.drawString(50, 720, f"Phone: {phone}")
            pdf.drawString(50, 705, f"Address: {address}")
            pdf.drawString(50, 690, "-" * 40)

            y = 670
            for i, item in enumerate(cart_list, start=1):
                pdf.drawString(50, y, f"{i}. {item['title']} x{item['qty']} = ${item['price']}")
                y -= 20

            pdf.drawString(50, y - 10, f"Total: ${total:.2f}")
            pdf.save()
            buffer.seek(0)

            # 🔹 3. Send PDF to Telegram
            send_pdf_to_telegram(buffer, filename=f"invoice_{date.today()}.pdf")

            flash('Order placed successfully! Invoice sent to your email and Telegram.', 'success')
            response = redirect(url_for('checkout'))
            response.set_cookie('clear_cart', '1', max_age=10)
            return response

        except Exception as e:
            flash(f'Failed to send invoice: {str(e)}', 'danger')

    return render_template('checkout.html')

@app.route('/product')
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


@app.get('/support')
def about():
    return render_template('support.html')




if __name__ == '__main__':
    app.run()