import time
from flask import Blueprint, request, session, url_for
from flask import render_template, redirect, jsonify
from authlib.integrations.flask_oauth2 import current_token
from .models import db, User, OAuth2Client
from .oauth2 import require_oauth


api_blueprint = Blueprint('api', __name__)

def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None


@api_blueprint.route('/profile')
@require_oauth('profile')
def me():
    user = current_token.user
    return jsonify(id=user.login)
