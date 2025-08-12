from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_mail import Message
import os, json, requests
from datetime import date
from config import mail, bot_token, chat_id, get_logo_base64
from invoice import send_pdf_to_telegram, generate_pdf_from_html

checkout_bp = Blueprint("checkout", __name__)

@checkout_bp.route('/checkout', methods=['GET', 'POST'])
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

        # Calculate totals
        subtotal = sum(item.get('qty', 0) * item.get('price', 0) for item in cart_list)
        shipping = 5.99 if cart_list else 0
        tax = round(subtotal * 0.1, 2)
        total = round(subtotal + shipping + tax, 2)

        logo_path = os.path.abspath("static/images/logo.png")
        logo_base64 = get_logo_base64()

        invoice_html = render_template('invoice_email.html',
                                       name=name,
                                       phone=phone,
                                       email=email,
                                       address=address,
                                       cart_list=cart_list,
                                       subtotal=subtotal,
                                       shipping=shipping,
                                       tax=tax,
                                       total=total,
                                       logo_path=logo_path,
                                       logo_base64=logo_base64
                                       )

        msg = Message(subject='Your Order Invoice',
                      recipients=[email],
                      html=invoice_html)
        try:
            mail.send(msg)

            # Telegram message with breakdown
            message_lines = [
                f"<strong>🧾 Invoice #{date.today().strftime('%Y%m%d')}</strong>",
                f"<code>👤 {name}</code>",
                f"<code>📧 {email}</code>",
                f"<code>📆 {date.today()}</code>",
                f"<code>🏠 {address}</code>",
                "<code>=======================</code>",
            ]
            for i, item in enumerate(cart_list, start=1):
                subtotal_item = item['qty'] * item['price']
                message_lines.append(
                    f"<code>{i}. {item['title']} x{item['qty']} = ${subtotal_item:.2f}</code>"
                )
            message_lines += [
                "<code>=======================</code>",
                f"<code>Subtotal: ${subtotal:.2f}</code>",
                f"<code>Shipping: ${shipping:.2f}</code>",
                f"<code>Tax (10%): ${tax:.2f}</code>",
                f"<code>💵 Total: ${total:.2f}</code>",
            ]

            telegram_message = "\n".join(message_lines)
            requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                data={"chat_id": chat_id, "text": telegram_message, "parse_mode": "HTML"}
            )

            # PDF generation for Telegram
            pdf_buffer = generate_pdf_from_html(invoice_html)
            send_pdf_to_telegram(pdf_buffer, filename=f"invoice_{date.today()}.pdf")

            flash('Order placed successfully! Invoice sent to your email and Telegram.', 'success')
            response = redirect(url_for('checkout.checkout'))
            response.set_cookie('clear_cart', '1', max_age=10)
            return response

        except Exception as e:
            flash(f'Failed to send invoice: {str(e)}', 'danger')

    return render_template('checkout.html')
