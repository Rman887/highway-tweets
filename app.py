from flask import Flask, render_template, url_for, session, redirect, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

from bs4 import BeautifulSoup
import requests

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'scrape_pages'
ALLOWED_EXTENSIONS = set(['txt', 'html'])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'this-is-a-secret-key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def scrape(text):
    soup = BeautifulSoup(text, "html.parser")
    links = soup.find_all("div", {"class": "js-tweet-text-container"})
    items = [x.prettify() for x in links]
    return items

@app.route('/', methods=['GET', 'POST'])
def main_page():

    items = []
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("File part missing")
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(full_path)

            try:
                with open(full_path, "r", encoding="utf8") as f:
                    items = scrape(f.read())
            except Exception as e:
                print("Error scraping file: ", e)
            else:
                os.remove(full_path)

    return render_template('index.html', items=items)


if __name__ == '__main__':
    app.run()
