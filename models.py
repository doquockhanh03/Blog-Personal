from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(50), default=datetime.utcnow)
    tags = db.Column(db.String(200), default="")
    desc = db.Column(db.Text, default="")
    content = db.Column(db.Text, default="")

class Work(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.String(10), default="")
    category = db.Column(db.String(120), default="")
    desc = db.Column(db.Text, default="")
    image = db.Column(db.String(255), default="")
