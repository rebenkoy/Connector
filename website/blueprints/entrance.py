from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required

from website.models import db, User, OAuth2Client
from website.login_manager import login_manager

entrance_blueprint = Blueprint('entrance', __name__)


login_manager.login_view = 'entrance.home'


@entrance_blueprint.route('/', methods=('GET', 'POST'))
def home():
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.query.filter_by(login=username).first()
        if not user:
            user = User(login=username)
            user.invalidate_token()
            db.session.add(user)
            db.session.commit()

        login_user(user)
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect('/')
    if current_user.is_authenticated:
        clients = OAuth2Client.query.filter_by(user_login=current_user.login).all()
    else:
        clients = []

    return render_template('home.html', user=current_user, clients=clients)


@entrance_blueprint.route('/logout')
def logout():
    current_user.invalidate_token()
    logout_user()
    return redirect('/')


@entrance_blueprint.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password_handler():
    if request.method == 'GET':
        return render_template('alterPass.html')

    new = request.form.get('password')
    confirmation = request.form.get('confirmation')
    if new == confirmation:
        current_user.alter_password(new)

        db.session.add(current_user)
        db.session.commit()
        return redirect(url_for("index"))
    return redirect(url_for("index"))

