# config.py
import os
import base64
from flask import Flask
from flask_mail import Mail
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv("EMAIL_USER"),
    MAIL_PASSWORD=os.getenv("EMAIL_PASS"),
    MAIL_DEFAULT_SENDER=('good day', os.getenv("EMAIL_USER")),
)

mail = Mail(app)

bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

# ----------------------------
# Shared photos folder
# ----------------------------

DB_PATH = r"D:\Dara\PythonAPI\exam\FlaskProject\site.db"
SHARED_PHOTO_FOLDER = r"D:\Dara\PythonAPI\exam\shared_photos"
os.makedirs(SHARED_PHOTO_FOLDER, exist_ok=True)

# ----------------------------
# Logo helper
# ----------------------------
def get_logo_base64():
    try:
        with open("static/images/logo.png", "rb") as img_file:
            return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode('utf-8')}"
    except Exception as e:
        print("Error encoding logo:", e)
        return ""
