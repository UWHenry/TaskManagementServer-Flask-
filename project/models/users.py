from datetime import datetime
from . import db
from flask_login import UserMixin

class Users(UserMixin, db.Model):
    __tablename__ = "users"
    username = db.Column(db.String, primary_key=True, index=True)
    password_hash = db.Column(db.String, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tasks = db.relationship('Tasks', backref='users', lazy=True, cascade='all, delete')
    
    def get_id(self):
        return str(self.username)
