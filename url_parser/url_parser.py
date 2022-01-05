import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .parser import parse_url

bp = Blueprint('auth', __name__, url_prefix='/')

@bp.route('/', methods=('GET', 'POST'))
def parse_url_page():
    url = "https://flask.palletsprojects.com/en/2.0.x/quickstart/"
    url = "https://stackoverflow.com/questions/67985120/how-to-pass-href-attribute-in-jinja2"
    url = "https://www.generacodice.com/en/articolo/452769/How-does-the-Jinja2-%238220%3Brecursive%238221%3B-tag-actually-work"
    url = "https://gosmoke.ru/"
    tree = parse_url(url=url)
    width = 20
    return render_template('index.html', tree=tree, width=width)