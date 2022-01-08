from flask import Blueprint, request
from flask import send_file, after_this_request, request, abort

# from .parser import clean_soup
from .parser import Parser, strip_scheme
import shutil
from .config import *

bp = Blueprint("url_parser", __name__, url_prefix="/")

parser = Parser(
    templates_path="url_parser/templates",
    caching=CACHE,
    caching_duration=CACHE_DURATION,
    cache_folder=CACHE_FOLDER,
)


@bp.route("/", methods=["GET"])
def parse_url_page():
    # Try to close temp file after request.
    @after_this_request
    def clean_up(response):
        try:
            tmp.close()
        except:
            pass
        return response

    # Display error if no url passed in query params.
    if not request.args.get("url"):
        abort(400, "You must specify url in get parameters")

    url = request.args.get("url")

    try:
        response = parser.get_and_check_url_response(url)
    except Exception as e:
        abort(e.args[0], e.args[1])

    width = int(request.args.get("width") or 200)
    img_flag = int(request.args.get("img") or 1)
    parser.img = img_flag
    file_name = parser.generate_file_name(url, width, img_flag)

    if parser.caching:
        cached_file_path = parser.generate_cache_path(url, width, img_flag)
        if parser.file_exists_in_cache(cached_file_path):
            return send_file(
                cached_file_path, as_attachment=True, attachment_filename=file_name
            )

    soup = parser.get_soup(response)
    cleaned_soup = parser.clean_soup(soup)
    rendered_template = parser.render_template(
        soup=cleaned_soup, width=width, img_flag=img_flag
    )

    tmp = parser.generate_txt_file(rendered_template)

    # Save tempfile on disk if caching enabled.
    if parser.caching:
        shutil.copyfile(tmp.name, cached_file_path)

    # Send file to the user.
    return send_file(tmp.name, as_attachment=True, attachment_filename=file_name)
