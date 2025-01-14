import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="dev",
    )

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
