from .extensions import db

'''
We will probably have a Class for User and Exercises here
'''


class Food(db.Model):
    id = db.Column(db.Integer, primery_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    protein = db.Column(db.Integer, nullable=False)
    carbs = db.Column(db.Integer, nullable=False)
    fats = db.Column(db.Integer, nullable=False)


class Excersie(db.Model2):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable= False)
    reps = db.Column(db.Integer, nullable=False)
    sets = db.Column(db.Integer, nullable=False)