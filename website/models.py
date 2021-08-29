import time
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.sqla_oauth2 import (
    OAuth2ClientMixin,
    OAuth2AuthorizationCodeMixin,
    OAuth2TokenMixin,
)
from flask_login import UserMixin
from werkzeug.security import gen_salt


db = SQLAlchemy()


class User(db.Model, UserMixin):
    login = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String)
    token = db.Column(db.String, unique=True)

    def __str__(self):
        return f'{self.login}@'

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

    def get_user_id(self):
        return self.login

    def check_password(self, password):
        print("NO IMPL: check_password")
        return True


class OAuth2Client(db.Model, OAuth2ClientMixin):
    __tablename__ = 'oauth2_client'

    id = db.Column(db.Integer, primary_key=True)
    user_login = db.Column(
        db.String(20),
        db.ForeignKey('user.login', ondelete='CASCADE'),
    )
    user = db.relationship('User')


class OAuth2AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
    __tablename__ = 'oauth2_code'

    id = db.Column(db.Integer, primary_key=True)
    user_login = db.Column(
        db.String(20),
        db.ForeignKey('user.login', ondelete='CASCADE'),
    )
    user = db.relationship('User')


class OAuth2Token(db.Model, OAuth2TokenMixin):
    __tablename__ = 'oauth2_token'

    id = db.Column(db.Integer, primary_key=True)
    user_login = db.Column(
        db.String(20),
        db.ForeignKey('user.login', ondelete='CASCADE'),
    )
    user = db.relationship('User')

    def is_refresh_token_active(self):
        if self.revoked:
            return False
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at >= time.time()