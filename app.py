import sys
sys.path.append(r"D:\Dara\PythonAPI\exam")

from flask import render_template, send_from_directory
from config import app, mail, SHARED_PHOTO_FOLDER  # use the instances already created
from route import blueprints

# ----------------------------
# Blueprints registration
# ----------------------------
for bp in blueprints:
    app.register_blueprint(bp)

# ----------------------------
# Routes
# ----------------------------
@app.route('/photos/<filename>')
def shared_photos(filename):
    return send_from_directory(SHARED_PHOTO_FOLDER, filename)

@app.route('/support')
def support():
    return render_template('support.html')

# ----------------------------
# Run
# ----------------------------
if __name__ == '__main__':
    app.run(debug=True)

