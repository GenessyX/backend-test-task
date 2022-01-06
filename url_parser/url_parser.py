import functools
from urllib import parse

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from flask import send_file, after_this_request, request, abort, jsonify

from .parser import parse_url
import tempfile
import os, shutil, time


bp = Blueprint('url_parser', __name__, url_prefix='/')

def strip_scheme(url):
    parsed = parse.urlparse(url).netloc + parse.urlparse(url).path
    return parsed.replace("/", "_")

@bp.route('/', methods=['GET'])
def parse_url_page():
    caching = current_app.config['CACHE']
    caching_duration = current_app.config['CACHE_DURATION']
    cache_folder = current_app.config['CACHE_FOLDER']

    @after_this_request
    def clean_up(response):
        try:
            tmp.close()
        except:
            pass
        return response

    if not request.args.get('url'):
        abort(400, "You must specify url in get parameters")

    url = request.args.get('url')

    if request.args.get('width'):
        width = int(request.args.get('width'))
    else:
        width = 200

    if request.args.get('img'):
        img_flag = int(request.args.get('img'))
    else:
        img_flag = 1

    file_name = strip_scheme(url) + '.txt'
    cached_file_path = os.path.abspath(os.path.join(cache_folder, file_name))
    # cached_file_path = os.path.abspath("cached/{}".format(file_name))

    if caching and os.path.isfile(cached_file_path) and (time.time() - os.path.getmtime(cached_file_path) < caching_duration):
        return send_file(cached_file_path, as_attachment=True, attachment_filename=file_name)

    tree = parse_url(url=url)
    rendered_template = render_template('response.txt.jinja', tree=tree, width=width, img_flag=img_flag)
    tmp = tempfile.NamedTemporaryFile()

    tmp.write(rendered_template.encode('utf-8'))

    if caching:
        shutil.copyfile(tmp.name, cached_file_path)


    return send_file(tmp.name, as_attachment=True, attachment_filename=file_name)

