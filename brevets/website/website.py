"""
Flask-Login and Flask-WTF example
"""
from urllib.parse import urlparse, urljoin
from flask import (Flask, request, render_template, redirect, url_for, flash,
                    abort, session)
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user, UserMixin,
                         confirm_login, fresh_login_required)
from flask_wtf import FlaskForm as Form
from wtforms import BooleanField, StringField, validators, PasswordField
from flask import Flask, render_template, request
import requests
from passlib.hash import sha256_crypt as pwd_context


class LoginForm(Form):
    username = StringField('Username', [
        validators.Length(min=2, max=25,
                          message=u"Huh, little too short for a username."),
        validators.InputRequired(u"Forget something?")])
    password = PasswordField('Password', [
        validators.Length(min=2, max=25,
                          message=u"Huh, little too short for a username."),
        validators.InputRequired(u"Forget something?")])
    remember = BooleanField('Remember me')


class RegistrationForm(Form):
    username = StringField('Username', [
        validators.Length(min=2, max=25,
                          message=u"Huh, little too short for a username."),
        validators.InputRequired(u"Forget something?")])
    password = PasswordField('Password', [
        validators.Length(min=2, max=25,
                          message=u"Huh, little too short for a username."),
        validators.InputRequired(u"Forget something?")])
    remember = BooleanField('Remember me')


def is_safe_url(target):
    """
    :source: https://github.com/fengsp/flask-snippets/blob/master/security/redirect_back.py
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


class User(UserMixin):
    def __init__(self, id, username, token):
        self.id = id
        self.username = username
        self.token = token


app = Flask(__name__)
app.secret_key = "and the cats in the cradle and the silver spoon"

app.config.from_object(__name__)

login_manager = LoginManager()

login_manager.session_protection = "strong"

login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."

login_manager.refresh_view = "login"
login_manager.needs_refresh_message = (
    u"To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return User(user_id, session.get("username"), session.get("token"))


login_manager.init_app(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/form")
@login_required
def form():
    return render_template("form.html")


@app.route('/list')
@login_required
def list():
    data = request.args.get("csv", type=str, default="json")
    k = request.args.get("k", type=int, default=-1)
    list_ = request.args.get("list", type=str)
    r = requests.get('http://restapi:5000/' + list_ + data + '?top=' + str(k) + '&token=' + session["token"])
    if r.status_code == 401:
        logout_user()
        return render_template("index.html")
    return r.text


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit() and request.method == "POST" and "username" in request.form and "password" in request.form:
        username = request.form["username"]
        password = pwd_context.using(salt="somestring").encrypt(request.form["password"])
        r = requests.post('http://restapi:5000/register?username=' + username + "&password=" + password)
        if r.status_code == 201:
            flash("Registered, you can login, logout and access api requests!")
            next = request.args.get("next")
            if not is_safe_url(next):
                abort(400)
            return redirect(next or url_for('index'))
        elif r.status_code == 400:
            flash(u"Registration fail.")
            abort(400)
        else:
            flash("Something went seriously wrong")
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit() and request.method == "POST" and "username" in request.form and "password" in request.form:
        username = request.form["username"]
        password = pwd_context.using(salt="somestring").encrypt(request.form["password"])
        response = requests.get('http://restapi:5000/token?username=' + username + "&password=" + password)
        if response.status_code == 201:
            token = response.json()
            remember = request.form.get("remember", "false") == "true"
            session["token"] = token["token"]
            session["username"] = username
            u = User(token["id"], session["username"], session["token"])
            if login_user(u, remember=remember):
                flash("Logged in!")
                flash("I'll remember you") if remember else None
                next = request.args.get("next")
                if not is_safe_url(next):
                    abort(401)
                return redirect(next or url_for('index'))
            else:
                flash("Sorry, but you could not log in.")
        else:
            flash(u"Invalid.")
            abort(401)
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
