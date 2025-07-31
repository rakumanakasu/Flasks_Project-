import requests

def send_pdf_to_telegram(pdf_bytes_io, filename='invoice.pdf'):
    import requests
    from os import getenv

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


