import json
import os
import sqlite3
import requests

from flask import Flask, redirect, request, url_for, render_template
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient

from src.app.database.db import get_db, init_db, close_db
from src.app.user import User
from src.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_DISCOVERY_URL


# Flask app setup
app = Flask(__name__)
app.secret_key = os.urandom(1024)

login_manager = LoginManager()
login_manager.init_app(app)

# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template('user.html', data=current_user)
    else:
        return render_template('index.html')


@app.route("/login")
def login_and_callback():
    # Find authorization endpoint
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Authorization request for the avaliable scopes
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code
    auth_code = request.args.get("code")

    # Find token endpoint endpoint
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Request to obtain tokens
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=auth_code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Using tokens to obtain user info
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    user_info_response = requests.get(uri, headers=headers, data=body)

    # Check email is verified
    if user_info_response.json().get("email_verified"):
        unique_id = user_info_response.json()["sub"]
        users_email = user_info_response.json()["email"]
        users_name = user_info_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    user = User(
        id_=unique_id, name=users_name, email=users_email
    )
    if not User.get(unique_id):
        user = User(unique_id, users_name, users_email)
        user.create()

    login_user(user)

    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":

    # Database setup
    try:
        init_db()
    # If database already created pass
    except sqlite3.OperationalError:
        pass

    app.run(host="0.0.0.0", port=80, debug=True, ssl_context=('cert.pem', 'key.pem'))
    close_db()
