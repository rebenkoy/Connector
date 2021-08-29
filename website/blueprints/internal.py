from flask import Blueprint, render_template
from flask_login import login_required, current_user

internal_blueprint = Blueprint('internal', __name__)


@internal_blueprint.route('/')
@login_required
def home():
    return render_template('index.html', user=current_user)
