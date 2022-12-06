from .extensions import db
from flask_login import UserMixin
from sqlalchemy.sql import func

'''
We will probably have a Class for User and Exercises here
'''


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    workouts = db.relationship('Workout')


'''
Fitness
'''


class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    data = db.Column(db.String(10000))
    exercises = db.relationship('Exercise')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    kind = db.Column(db.String(50), nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'))


'''
Nutrition
'''


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    protein = db.Column(db.Integer, nullable=False)
    carbs = db.Column(db.Integer, nullable=False)
    fats = db.Column(db.Integer, nullable=False)
