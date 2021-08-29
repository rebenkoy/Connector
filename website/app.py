import os
import typing

import flask
from flask import Flask


def create_app(config=None):
    app = Flask(__name__)

    # load default configuration
    app.config.from_object('website.settings')

    # load environment configuration
    if 'WEBSITE_CONF' in os.environ:
        app.config.from_envvar('WEBSITE_CONF')

    # load app specified configuration
    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py'):
            app.config.from_pyfile(config)

    return app


def setup_app(
        app: flask.Flask,
        blueprints: typing.Dict[str, flask.Blueprint],
        db,
        login_manager,
        config_oauth,
):
    # Create tables if they do not exist already
    @app.before_first_request
    def create_tables():
        db.create_all()

    db.init_app(app)
    login_manager.init_app(app)
    config_oauth(app)
    for prefix, bp in blueprints.items():
        app.register_blueprint(bp, url_prefix=prefix)