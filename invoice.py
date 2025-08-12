import requests
import io
from xhtml2pdf import pisa
from os import getenv

def send_pdf_to_telegram(pdf_bytes_io, filename='invoice.pdf'):
    url = f"https://api.telegram.org/bot{getenv('BOT_TOKEN')}/sendDocument"
    files = {
        'document': (filename, pdf_bytes_io)
    }
    data = {
        'chat_id': getenv('CHAT_ID'),
        'caption': '🧾 New Order Invoice'
    }
    try:
        response = requests.post(url, data=data, files=files)
        return response.ok
    except Exception as e:
        print("Failed to send PDF:", e)
        return False

def generate_pdf_from_html(html_content):
    pdf_stream = io.BytesIO()
    pisa.CreatePDF(html_content, dest=pdf_stream)
    pdf_stream.seek(0)
    return pdf_stream
