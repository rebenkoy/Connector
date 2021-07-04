import random
import time
import datetime

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, flash, url_for, redirect, render_template
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user

from werkzeug.security import generate_password_hash, check_password_hash, gen_salt

flask_app = Flask(__name__, template_folder="static")
flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
flask_app.config['SECRET_KEY'] = '123123123'
flask_app.config['REMEMBER_COOKIE_DOMAIN'] = '.redanvil.keenetic.pro' # needs testing
db = SQLAlchemy(flask_app)
login_manager = LoginManager(flask_app)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    login = db.Column(db.String, unique=True, primary_key=True)
    password = db.Column(db.String)
    token = db.Column(db.String, unique=True)

    def get_id(self):
        try:
            return self.token
        except AttributeError:
            raise NotImplementedError('No `login` attribute - override `get_id`')

    @classmethod
    def get_user(cls, login):
        return db.session.query(cls).get(login)

    def invalidate_token(self):
        self.token = gen_salt(64)

    def alter_password(self, new_password):
        self.password = new_password
        self.invalidate_token()


db.create_all()


@login_manager.user_loader
def load_user(token):
    return db.session.query(User).filter_by(token=token).first()


login_manager.login_view = "login_handler"


def is_safe_url(*args, **kwargs): # will be done later
    return True


@flask_app.route("/")
def index():
    return render_template(
        'index.html',
        login=current_user.login + '@' if current_user.is_authenticated else 'darkness',
        login_url=url_for("login_handler"),
        logout_url=url_for("logout_handler"),
        change_password_url=url_for("change_password_handler"),
    )


@flask_app.route('/login', methods=['GET', 'POST'])
def login_handler():
    if request.method == 'GET':
        return render_template('login.html')

    login = request.form.get('login')
    password = request.form.get('password')
    remember = request.form.get('remember')

    user = User.get_user(login)
    if user is None:
        time.sleep(random.random() * 0.1)  # fine tuning to mimic base search (FOR SECURITY)
        return abort(401)
    if password == user.password:
        login_user(user, remember=remember)

        flash('Logged in successfully.')

        next_url = request.args.get('next')
        if not is_safe_url(next_url):
            return abort(400)

        return redirect(next_url or url_for("index"))
    else:
        return abort(401)


@flask_app.route('/logout')
@login_required
def logout_handler():
    current_user.invalidate_token()
    logout_user()
    return redirect(url_for('index'))


@flask_app.route('/change_password', methods=['GET', 'POST'])
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
    flash('Passwords do not match')
    return redirect(url_for("index"))