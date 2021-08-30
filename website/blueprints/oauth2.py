import time

from flask import Blueprint, request, url_for, render_template, redirect
from flask_login import current_user, login_required
from authlib.oauth2 import OAuth2Error
from werkzeug.security import gen_salt

from website.models import db, User, OAuth2Client
from website.oauth2 import authorization


oauth2_blueprint = Blueprint('oauth', __name__)


def split_by_crlf(s):
    return [v for v in s.splitlines() if v]


@oauth2_blueprint.route('/create_client', methods=('GET', 'POST'))
@login_required
def create_client():
    if request.method == 'GET':
        return render_template('create_client.html', user=current_user)

    client_id = gen_salt(24)
    client_id_issued_at = int(time.time())
    client = OAuth2Client(
        client_id=client_id,
        client_id_issued_at=client_id_issued_at,
        user_login=current_user.login,
    )

    form = request.form
    client_metadata = {
        "client_name": form["client_name"],
        "client_uri": form["client_uri"],
        "grant_types": split_by_crlf(form["grant_type"]),
        "redirect_uris": split_by_crlf(form["redirect_uri"]),
        "response_types": split_by_crlf(form["response_type"]),
        "scope": form["scope"],
        "token_endpoint_auth_method": form["token_endpoint_auth_method"]
    }
    client.set_client_metadata(client_metadata)

    if form['token_endpoint_auth_method'] == 'none':
        client.client_secret = ''
    else:
        client.client_secret = gen_salt(48)

    db.session.add(client)
    db.session.commit()
    return redirect('/')


@oauth2_blueprint.route('/authorize', methods=['GET', 'POST'])
@login_required
def authorize():
    user = current_user
    # if user log status is not true (Auth server), then to log it in
    if not user:
        return redirect(url_for('website.routes.home', next=request.url))
    if request.method == 'GET':
        try:
            grant = authorization.validate_consent_request(end_user=user)
        except OAuth2Error as error:
            return error.error
        return render_template('authorize.html', user=user, grant=grant)
    if not user and 'username' in request.form:
        username = request.form.get('username')
        user = User.query.filter_by(login=username).first()
    if request.form['confirm']:
        grant_user = user
    else:
        grant_user = None
    return authorization.create_authorization_response(grant_user=grant_user)


@oauth2_blueprint.route('/token', methods=['POST'])
def issue_token():
    return authorization.create_token_response()


@oauth2_blueprint.route('/revoke', methods=['POST'])
def revoke_token():
    return authorization.create_endpoint_response('revocation')

