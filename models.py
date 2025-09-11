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

class Roadmap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    # stages được xóa theo roadmap
    stages = db.relationship('Stage', backref='roadmap', cascade="all, delete-orphan", order_by="Stage.order")

class Stage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roadmap_id = db.Column(db.Integer, db.ForeignKey('roadmap.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)  # sắp xếp stage

    tasks = db.relationship('Task', backref='stage', cascade="all, delete-orphan", order_by="Task.id")

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stage_id = db.Column(db.Integer, db.ForeignKey('stage.id'))
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    is_done = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)  # ← thêm dòng này

