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
        # -------------------------
        # Collect form data
        # -------------------------
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        cart_json = request.form.get('cart_data', '[]')

        # -------------------------
        # Parse cart JSON safely
        # -------------------------
        try:
            cart_list = json.loads(cart_json)
            if not isinstance(cart_list, list):
                cart_list = []
        except Exception as e:
            print("Cart JSON parse error:", e)
            cart_list = []

        # -------------------------
        # Ensure items have proper fields
        # -------------------------
        for item in cart_list:
            item['title'] = str(item.get('title', 'Unknown'))
            item['qty'] = float(item.get('qty', 1))
            item['price'] = float(item.get('price', 0))
            item['image'] = str(item.get('image', ''))

        # -------------------------
        # Calculate totals
        # -------------------------
        subtotal = sum(item['qty'] * item['price'] for item in cart_list)
        shipping = 5.99 if cart_list else 0
        tax = round(subtotal * 0.1, 2)
        total = round(subtotal + shipping + tax, 2)

        # -------------------------
        # Generate invoice HTML
        # -------------------------
        try:
            logo_base64 = get_logo_base64() or ''
        except Exception as e:
            print("Logo base64 error:", e)
            logo_base64 = ''

        invoice_html = render_template(
            'invoice_email.html',
            name=name,
            phone=phone,
            email=email,
            address=address,
            cart_list=cart_list,
            subtotal=subtotal,
            shipping=shipping,
            tax=tax,
            total=total,
            logo_base64=logo_base64
        )

        # -------------------------
        # Send Email
        # -------------------------
        try:
            msg = Message(
                subject=f"Your Order Invoice #{date.today().strftime('%Y%m%d')}",
                recipients=[email],
                html=invoice_html
            )
            mail.send(msg)
        except Exception as e:
            print("Mail send error:", e)
            flash(f'Failed to send email: {str(e)}', 'danger')
            return render_template('checkout.html')

        # -------------------------
        # Send Telegram summary (text only, no URLs)
        # -------------------------
        try:
            message_lines = [
                f"<strong>🧾 Invoice #{date.today().strftime('%Y%m%d')}</strong>",
                f"<code>👤 {name}</code>",
                f"<code>📧 {email}</code>",
                f"<code>📆 {date.today()}</code>",
                f"<code>🏠 {address}</code>",
                "<code>=======================</code>"
            ]

            for i, item in enumerate(cart_list, start=1):
                subtotal_item = item['qty'] * item['price']
                message_lines.append(
                    f"<code>{i}. {item['title']} x{int(item['qty'])} = ${subtotal_item:.2f}</code>"
                )

            message_lines += [
                "<code>=======================</code>",
                f"<code>Subtotal: ${subtotal:.2f}</code>",
                f"<code>Shipping: ${shipping:.2f}</code>",
                f"<code>Tax (10%): ${tax:.2f}</code>",
                f"<code>💵 Total: ${total:.2f}</code>"
            ]

            telegram_message = "\n".join(message_lines)
            requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                data={"chat_id": chat_id, "text": telegram_message, "parse_mode": "HTML"}
            )
        except Exception as e:
            print("Telegram summary error:", e)

        # -------------------------
        # Send each product image as separate Telegram photo
        # -------------------------
        try:
            for item in cart_list:
                image_url = item.get('image', '')
                if image_url:
                    caption = f"{item['title']} x{int(item['qty'])} - ${item['qty'] * item['price']:.2f}"
                    requests.post(
                        f"https://api.telegram.org/bot{bot_token}/sendPhoto",
                        data={
                            "chat_id": chat_id,
                            "photo": image_url,
                            "caption": caption,
                            "parse_mode": "HTML"
                        }
                    )
        except Exception as e:
            print("Telegram send photo error:", e)

        # -------------------------
        # Generate PDF and send to Telegram
        # -------------------------
        try:
            pdf_buffer = generate_pdf_from_html(invoice_html)
            send_pdf_to_telegram(pdf_buffer, filename=f"invoice_{date.today()}.pdf")
        except Exception as e:
            print("PDF/Telegram send error:", e)

        # -------------------------
        # Success flash & clear cart
        # -------------------------
        flash('Order placed successfully! Invoice sent to your email and Telegram.', 'success')
        response = redirect(url_for('checkout.checkout'))
        response.set_cookie('clear_cart', '1', max_age=10)
        return response

    # -------------------------
    # GET request
    # -------------------------
    return render_template('checkout.html')
