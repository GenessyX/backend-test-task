import functools
from urllib import parse

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from flask import send_file, after_this_request

from .parser import parse_url
import tempfile


bp = Blueprint('auth', __name__, url_prefix='/')

@bp.route('/', methods=('GET', 'POST'))
def parse_url_page():

    @after_this_request
    def clean_up(response):
        tmp.close()
        return response

    url = "https://flask.palletsprojects.com/en/2.0.x/quickstart/"
    url = "https://stackoverflow.com/questions/67985120/how-to-pass-href-attribute-in-jinja2"
    url = "https://www.generacodice.com/en/articolo/452769/How-does-the-Jinja2-%238220%3Brecursive%238221%3B-tag-actually-work"
    url = "https://gosmoke.ru/"
    # url = "https://stackoverflow.com/questions/12166970/in-python-using-flask-how-can-i-write-out-an-object-for-download"

    tree = parse_url(url=url)
    width = 50
    rendered_template = render_template('response.txt.jinja', tree=tree, width=width)
    tmp = tempfile.NamedTemporaryFile()

    tmp.write(rendered_template.encode('utf-8'))

    return send_file(tmp.name, as_attachment=True, attachment_filename="test.txt")


@bp.route('/get_file')
def parse_url_to_file():
    url = "https://stackoverflow.com/questions/12166970/in-python-using-flask-how-can-i-write-out-an-object-for-download"
    tree = parse_url(url=url)
    width = 20
    return current_app.response_class(stream_template('response.txt', tree=tree, width=width))

