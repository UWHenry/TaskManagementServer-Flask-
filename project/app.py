import os

from flask import Flask, request, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import db
from models.tasks import Tasks
from authenication import argon2, login_manager, limiter, auth_blueprint


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['DEBUG'] = True

argon2.init_app(app)
login_manager.init_app(app)
limiter.init_app(app)


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db.init_app(app) 
with app.app_context():
    db.create_all()

app.register_blueprint(auth_blueprint)

@app.route('/')
def index():
    return redirect(url_for("dashboard"))

@app.route('/dashboard')
@login_required
def dashboard():
    tasks = current_user.tasks
    content = {
        "username": current_user.username,
    }
    # render the dashboard page for authenticated users only
    return render_template('dashboard.html', content=content)

@app.route('/add_task')
@login_required
def add_task():
    task = {
        "name": "",
        "description": "",
        "deadline": ""
    }
    if request.method == 'POST':
        name = request.form["name"]
        description = request.form["description"]
        deadline = request.form["deadline"]
        new_task = Tasks(
            name = name,
            description = description,
            deadline = deadline,
            completed = False,
            user = current_user.username
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("dashboard")) 
    return render_template('add_task.html')

if __name__ == '__main__':
    app.run(debug=True)