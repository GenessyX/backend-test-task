from urllib import parse
from bs4 import BeautifulSoup

from flask import (
    Blueprint, render_template, request, current_app
)
from flask import send_file, after_this_request, request, abort

from .parser import clean_soup
import tempfile
import os, shutil, time
import requests

bp = Blueprint('url_parser', __name__, url_prefix='/')

def strip_scheme(url):
    parsed = parse.urlparse(url).netloc + parse.urlparse(url).path
    return parsed.replace("/", "_")

@bp.route('/', methods=['GET'])
def parse_url_page():
    caching = current_app.config['CACHE']
    caching_duration = current_app.config['CACHE_DURATION']
    cache_folder = current_app.config['CACHE_FOLDER']

    # Try to close temp file after request.
    @after_this_request
    def clean_up(response):
        try:
            tmp.close()
        except:
            pass
        return response

    # Display error if no url passed in query params.
    if not request.args.get('url'):
        abort(400, "You must specify url in get parameters")

    url = request.args.get('url')

    # Check if url returns ok code.
    r = requests.get(url)
    st_code = r.status_code
    if not st_code == requests.codes.ok:
        abort(st_code, "Url returned: {} status code".format(str(st_code)))

    # Width parameter.
    if request.args.get('width'):
        width = int(request.args.get('width'))
    else:
        # Defalut value
        width = 200

    # Img_flag (parse images or not).
    if request.args.get('img'):
        img_flag = 1 if int(request.args.get('img')) else 0
    else:
        # Default value
        img_flag = 1

    # Generate file name for download.
    file_name = strip_scheme(url) + '_w-' + str(width) + '_i-' + str(img_flag) + '.txt'

    if caching:
        cached_file_path = os.path.abspath(os.path.join(cache_folder, file_name))

    if caching and os.path.isfile(cached_file_path) and (time.time() - os.path.getmtime(cached_file_path) < caching_duration):
        # If caching enabled and cached file exists and was created less than caching duration ago.
        # Return cached file.
        return send_file(cached_file_path, as_attachment=True, attachment_filename=file_name)

    tree = BeautifulSoup(r.content, 'html.parser')
    tree = clean_soup(tree)

    # print(tree)
    # print(type(tree))
    # print(list(tree.children))

    # Generate txt file.
    rendered_template = render_template('response.txt.jinja', tree=tree, width=width, img_flag=img_flag)

    # Create temporary file and write generated txt to it.
    tmp = tempfile.NamedTemporaryFile()
    tmp.write(rendered_template.encode('utf-8'))
    tmp.seek(0, 2)


    # Save tempfile on disk if caching enabled.
    if caching:
        shutil.copyfile(tmp.name, cached_file_path)

    # Send file to the user.
    return send_file(tmp.name, as_attachment=True, attachment_filename=file_name)

