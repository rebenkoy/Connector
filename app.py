
from website.app import create_app, setup_app
from website.oauth2 import config_oauth
from website.models import db
from website.login_manager import login_manager
from website.routes import api_blueprint
from website.blueprints.entrance import entrance_blueprint
from website.blueprints.oauth2 import oauth2_blueprint

app = create_app({
    'SECRET_KEY': 'secret',
    'OAUTH2_REFRESH_TOKEN_GENERATOR': True,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///db.sqlite',
})

setup_app(
    app,
    {
        '/': entrance_blueprint,
        '/oauth': oauth2_blueprint,
        '/api': api_blueprint,
    },
    db,
    login_manager,
    config_oauth,
)
