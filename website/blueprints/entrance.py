from flask import Blueprint, request, render_template, redirect, url_for, abort
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from website.models import db, User, OAuth2Client
from website.login_manager import login_manager

entrance_blueprint = Blueprint('entrance', __name__)


login_manager.login_view = 'entrance.home'


@entrance_blueprint.route('/', methods=('GET', 'POST'))
def home():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        remember = request.form.get('remember')
        user = User.get_user(login)

        if user is None:
            user = User(login=login)
            user.invalidate_token()
            user.password = generate_password_hash(password, 'sha256')
            db.session.add(user)
            db.session.commit()
        if not check_password_hash(user.password, password):
            return abort(401)

        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)

        return redirect(url_for('internal.home'))
    if current_user.is_authenticated:
        return redirect(url_for('internal.home'))

    return render_template('login.html')


@entrance_blueprint.route('/logout')
def logout():
    current_user.invalidate_token()
    logout_user()
    return redirect('/')


@entrance_blueprint.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'GET':
        return render_template('alterPass.html')

    new = request.form.get('password')
    confirmation = request.form.get('confirmation')
    if new == confirmation:
        current_user.alter_password(generate_password_hash(new, 'sha256'))

        db.session.add(current_user)
        db.session.commit()
    return redirect(url_for("internal.home"))

