import os
from flask import Flask, render_template, request, redirect, flash, url_for, session, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from core.cutdetector import predict
from core.model.softcut import softcut

app = Flask(__name__)
app.secret_key = "super secret key"
CORS(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")

@app.route("/upload", methods=['GET','POST'])
def submit_file():
    if request.method == 'POST' or request.method == 'GET':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER,filename))
            print("Working on {}".format(filename))
            hc, sc = predict(0.75, 1, 100, '/home/tre3x/Python/FilmEditsDetection/backend/core/model/trainedmodel').run(os.path.join(UPLOAD_FOLDER,filename), True)
            flash(hc)
            flash(sc)
            return jsonify(hc, sc)

            
if __name__ == "__main__":
    app.debug = True
    app.run()