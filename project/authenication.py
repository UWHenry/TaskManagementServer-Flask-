from flask import request, Blueprint, render_template, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_argon2 import Argon2
from sqlalchemy.exc import IntegrityError

from models import db
from models.users import Users

auth_blueprint = Blueprint('auth_blueprint', __name__)
argon2 = Argon2()
login_manager = LoginManager()
login_manager.login_view = 'auth_blueprint.login'
limiter = Limiter(key_func=get_remote_address)

@login_manager.user_loader
def load_user(username):
    return Users.query.get(username)

@auth_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    content = {
        "username": "",
        "error_msg": "",
        "login_url": url_for('auth_blueprint.login'),
        "signup_url": url_for('auth_blueprint.signup')
    }
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        content["username"] = username
        
        db_user = load_user(username)
        if username == "":
            content["error_msg"] = "Username can not be empty!"
        elif db_user is not None:
            content["error_msg"] = "Username already exists!"
        elif password == "":
            content["error_msg"] = "Password can not be empty!"
        elif password != confirm_password:
            content["error_msg"] = "Password and Confirm Password does not match!"
        else:
            success = _add_user(username, password)
            if success: 
                login_user(load_user(username))
                return redirect(url_for("task_blueprint.dashboard"))
            content["error_msg"] = "Username already exists!"
    return render_template('signup.html', content=content)

def _add_user(username: str, password: str) -> bool:
    try:
        password_hash = argon2.generate_password_hash(password)
        new_user = Users(
            username = username,
            password_hash = password_hash
        )
        db.session.add(new_user)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False

@auth_blueprint.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    content = {
        "username": "",
        "error_msg": "",
        "signup_url": url_for('auth_blueprint.signup'),
        "login_url": url_for('auth_blueprint.login')
    }
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        db_user = load_user(username)
        if username == "":
            content["error_msg"] = "Username can not be empty!"
        elif password == "":
            content["error_msg"] = "Password can not be empty!"
        elif db_user is None:
            content["error_msg"] = "Username does not exist!"
        else:
            correct = argon2.check_password_hash(db_user.password_hash, password)
            if correct:
                login_user(db_user)
                return redirect(url_for("task_blueprint.dashboard"))
            content["error_msg"] = "Wrong password, please try again!"
    return render_template('login.html', content=content)

@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    content = {
        "message": "Log out is successful!",
        "redirect_url": url_for("index"),
        "delay": 3
    }
    return render_template('logout.html', content=content)