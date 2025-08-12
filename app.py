from flask import Flask, render_template
from flask_mail import Mail
from dotenv import load_dotenv
import os
from route import blueprints

app = Flask(__name__)
load_dotenv()

app.secret_key = os.getenv("SECRET_KEY")

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("EMAIL_USER")
app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASS")
app.config['MAIL_DEFAULT_SENDER'] = ('good day', app.config['MAIL_USERNAME'])

mail = Mail(app)

for bp in blueprints:
    app.register_blueprint(bp)

@app.route('/support')
def about():
    return render_template('support.html')

if __name__ == '__main__':
    app.run(debug=True)
