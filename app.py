from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)


@app.route('/')
def main_page():
    page = requests.get('https://github.com/Rman887/highway-tweets')

    soup = BeautifulSoup(page.text, "html.parser")

    links = soup.find_all('a')

    link_list = [x.prettify() for x in links]

    return render_template('index.html', text=link_list)


if __name__ == '__main__':
    app.run()
