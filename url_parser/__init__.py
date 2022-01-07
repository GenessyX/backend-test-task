import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    # Configure caching.
    app.config["CACHE_FOLDER"] = "cache"
    app.config["CACHE"] = 0
    app.config["CACHE_DURATION"] = 12 * 60 * 60  # 12 hrs.

    # Trim whitespaces from generated txt
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the cache folder exists
    try:
        os.makedirs(app.config["CACHE_FOLDER"])
    except OSError:
        pass

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # url parser page
    from . import url_parser

    app.register_blueprint(url_parser.bp)

    return app
