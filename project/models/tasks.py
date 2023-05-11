from datetime import datetime
from . import db

class Tasks(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    create_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    deadline = db.Column(db.DateTime)
    completed = db.Column(db.Boolean)
    user = db.Column(db.String, db.ForeignKey("users.username", ondelete="CASCADE"), nullable=False)