from datetime import datetime

from flask import request, Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
import pandas as pd

from models import db
from models.tasks import Tasks


task_blueprint = Blueprint('task_blueprint', __name__)

@task_blueprint.route('/dashboard')
@login_required
def dashboard():
    columns = ["id", "name", "description", "deadline"]
    tasks = current_user.tasks
    tasks_df = pd.DataFrame.from_records([task.__dict__ for task in tasks])
    if tasks_df.empty:
        tasks_df = pd.DataFrame(columns=columns)
    else:
        tasks_df = tasks_df[(tasks_df["enabled"] == True) & (tasks_df["completed"] == False)]
        tasks_df = tasks_df[columns]
    tasks_df = tasks_df.rename(columns=lambda x: x.title())
    content = {
        "username": current_user.username,
        "table": tasks_df,
        "add_task_url": url_for('task_blueprint.add_task'),
        "logout_url": url_for('auth_blueprint.logout'),
        "alter_task_url": url_for('task_blueprint.alter_task')
    }
    return render_template('dashboard.html', content=content)

@task_blueprint.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    content = {
        "add_task_url": url_for('task_blueprint.add_task'),
        "dashboard_url": url_for("task_blueprint.dashboard")
    }
    if request.method == 'POST':
        name = request.form["name"]
        description = request.form["description"]
        deadline = request.form["deadline"]
        if not deadline:
            deadline = None
        new_task = Tasks(
            name = name,
            description = description,
            deadline = deadline,
            completed = False,
            user = current_user.username
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("task_blueprint.dashboard")) 
    return render_template('add_task.html', content=content)

@task_blueprint.route('/alter_task', methods=['POST'])
@login_required
def alter_task():
    completed = request.form.get("completed", None)
    edit = request.form.get("edit", None)
    delete = request.form.get("delete", None)
    if completed:
        task = Tasks.query.get(completed)
        task.completed = True
    elif delete:
        task = Tasks.query.get(delete)
        task.enabled = False
    else:
        return redirect(url_for("task_blueprint.edit_task", id=edit))
    db.session.commit()
    return redirect(url_for("task_blueprint.dashboard"))

@task_blueprint.route('/edit_task', methods=['GET', 'POST'])
@login_required
def edit_task():
    task_id = request.args.get('id')
    if request.method == 'POST':
        task_id = request.form["submit"]
    task = Tasks.query.get(task_id)
    if not task or task.user != current_user.username or task.completed or not task.enabled:
        return redirect(url_for("task_blueprint.dashboard"))
    
    content = {
        "name": task.name,
        "description": task.description,
        "deadline": task.deadline,
        "task_id": task_id,
        "edit_task_url": url_for('task_blueprint.edit_task'),
        "dashboard_url": url_for('task_blueprint.dashboard')
    }
    if request.method == 'POST':
        name = request.form["name"]
        description = request.form["description"]
        deadline = request.form["deadline"]
        if not deadline:
            deadline = None
        task.name = name
        task.description = description
        task.deadline = deadline
        task.last_modified = datetime.now()        
        db.session.commit()
        return redirect(url_for("task_blueprint.dashboard")) 
    return render_template('edit_task.html', content=content)
