from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash, gen_salt

from website.models import db, User


login_manager = LoginManager()


@login_manager.user_loader
def load_user(token):
    return db.session.query(User).filter_by(token=token).first()
