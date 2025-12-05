from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)       
    unique_id = db.Column(db.String(50), unique = True, nullable=True)     
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.String(50), nullable=False)   
    end_date = db.Column(db.String(50), nullable=False)     
    start_time = db.Column(db.String(20), nullable=False)
    end_time = db.Column(db.String(20), nullable=False)
    image_file = db.Column(db.String(100), nullable=False, default='default.jpg')
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    registrations = db.relationship('Registration', backref='event', lazy=True, cascade="all, delete-orphan")

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    student = db.relationship('User', backref='registrations', lazy=True) 
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))