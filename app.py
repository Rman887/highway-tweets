from flask import Flask, render_template, url_for, session, redirect, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

from bs4 import BeautifulSoup
import requests

import os
from werkzeug.utils import secure_filename
import re

UPLOAD_FOLDER = 'scrape_pages'
ALLOWED_EXTENSIONS = set(['txt', 'html'])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'this-is-a-secret-key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def scrape_post(post):
    print(post)
    author_name_tag = post.find("strong", {"class": "fullname"})
    author_username_tag = post.find("span", {"class": "username"})
    contents_tag = post.find("p", {"class": "tweet-text"})
    retweets_tag = post.find("button", {"class": "js-actionRetweet"})
    likes_tag = post.find("button", {"class": "js-actionFavorite"})
    url_tag = post.find("a", {"class": "tweet-timestamp"})

    print("=====")
    print(author_name_tag)
    print(author_username_tag)

    data = {}
    if author_name_tag and not author_name_tag.is_empty_element:
        data["author_name"] = author_name_tag.get_text().strip()
    if author_username_tag and not author_username_tag.is_empty_element:
        data["author_username"] = author_username_tag.get_text().strip()
    if contents_tag and not contents_tag.is_empty_element:
        data["contents"] = contents_tag.get_text().strip()
    if retweets_tag and not retweets_tag.is_empty_element:
        data["retweets"] = re.findall(r'\d+', retweets_tag.get_text())
        if len(data["retweets"]) > 0:
            data["retweets"] = int(data["retweets"][0])
        else:
            data.pop("retweets")
    if likes_tag and not likes_tag.is_empty_element:
        data["likes"] = re.findall(r'\d+', likes_tag.get_text())
        if len(data["likes"]) > 0:
            data["likes"] = int(data["likes"][0])
        else:
            data.pop("likes")
    if url_tag and not url_tag.is_empty_element and url_tag.has_attr("href"):
        data["url"] = url_tag["href"].strip()

    return data


def scrape_page(text):
    soup = BeautifulSoup(text, "html.parser")

    posts = soup.find_all("li", {"class": "stream-item"})
    items = []
    for post in posts:
        if not post.is_empty_element:
            items.append(scrape_post(post))
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
                    items = scrape_page(f.read())
            except Exception as e:
                print("Error scraping file: ", e)
                raise
            else:
                os.remove(full_path)

    return render_template('index.html', items=items)


if __name__ == '__main__':
    app.run()
