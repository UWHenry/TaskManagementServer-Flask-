import os

from flask import Flask, redirect, url_for

from models import db
from authenication import argon2, login_manager, limiter, auth_blueprint
from task import task_blueprint


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

argon2.init_app(app)
login_manager.init_app(app)
limiter.init_app(app)


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db.init_app(app) 
with app.app_context():
    db.create_all()

app.register_blueprint(auth_blueprint)
app.register_blueprint(task_blueprint)

@app.route('/')
def index():
    return redirect(url_for("task_blueprint.dashboard"))


if __name__ == '__main__':
    app.run()