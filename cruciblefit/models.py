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
    weight = db.Column(db.Integer, nullable=False, default=100)
    height = db.Column(db.Integer, nullable=False, default=68)
    dob = db.Column(db.Date, nullable=False, default=func.now())
    workouts = db.relationship('Workout')
    foods = db.relationship('Food')  # added
    meals = db.relationship('Meal')

    @property
    def age(self):
        return int((func.now() - self.dob).days / 365.25)


'''
Fitness
'''


class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    data = db.Column(db.String(10000))
    exercises = db.relationship('Exercise')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @property
    def total_calories(self):
        total = 0
        for exercise in self.exercises:
            total += exercise.calories
        return total


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=True, default='cardio')
    reps = db.Column(db.Integer, nullable=False, default=0)
    sets = db.Column(db.Integer, nullable=False, default=0)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'))

    @property
    def calories(self):
        if self.type == 'cardio':
            return self.reps * self.sets * 4
        else:
            return self.reps * self.sets * 2


'''
Nutrition
'''


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False, default='food item')
    protein = db.Column(db.Integer, nullable=False, default=0)
    carbs = db.Column(db.Integer, nullable=False, default=0)
    fats = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # added

    @property
    def calories(self):
        protein_calc = self.protein * 4
        carbs_calc = self.carbs * 4
        fats_calc = self.fats * 9
        total_calories = protein_calc + carbs_calc + fats_calc
        return total_calories


# Many-to-Many relationship
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
# Limitations: you can only add one food at a time. Can only add one food per day
meal_food_many_to_many = db.Table('log_items',
                                  db.Column('id', db.Integer, primary_key=True),
                                  db.Column('meal_id', db.Integer, db.ForeignKey('meal.id')),
                                  db.Column('food_id', db.Integer, db.ForeignKey('food.id'))
                                  )


class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    foods = db.relationship('Food', secondary=meal_food_many_to_many, lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @property
    def total_calories(self):
        total = 0
        for item in self.foods:
            total += item.calories
        return total
