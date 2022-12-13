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
    exercises = db.relationship('Exercise')
    foods = db.relationship('Food')  # added
    meals = db.relationship('Meal')

    @property
    def age(self):
        return int((func.now() - self.dob).days / 365.25)


'''
Fitness
'''


class WorkoutExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout = db.relationship('Workout', back_populates='exercises_link')
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'))
    exercise = db.relationship('Exercise', back_populates='workouts_link')
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'))


class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercises_link = db.relationship('WorkoutExercise', back_populates='workout', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    data = db.Column(db.String(10000))

    @property
    def get_exercises(self):
        exercises = []
        for item in self.exercises_link:
            if item.exercise:
                exercises.append([item.exercise, item.id])
            else:
                db.session.delete(item)
                db.session.commit()
        return exercises

    def add_exercise(self, exercise_id):
        self.exercises_link.append(WorkoutExercise(exercise_id=exercise_id))
        db.session.commit()

    def remove_exercise(self, workout_exercise_id):
        """
        Removes an exercise from the workout
        :param workout_exercise_id:
        :return:
        """
        try:
            workout_exercise = WorkoutExercise.query.filter_by(id=workout_exercise_id).first()
            db.session.delete(workout_exercise)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            return False
        # workout_exercise = WorkoutExercise.query.get(workout_exercise_id)
        # self.exercises_link.remove(workout_exercise)
        # db.session.commit()

    @property
    def total_cals_burned(self):
        total = 0
        for exercise in self.exercises_link:
            total += exercise.calories
        return total


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    workouts_link = db.relationship('WorkoutExercise', back_populates='exercise', lazy='dynamic')
    name = db.Column(db.String(50), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=True, default='cardio')
    sets = db.Column(db.Integer, nullable=False, default=0)
    reps = db.Column(db.Integer, nullable=False, default=0)
    weight = db.Column(db.Integer, nullable=False, default=0)

    @property
    def cals_burned(self):
        if self.type == 'cardio':
            return self.reps * self.sets * 4
        else:
            return self.reps * self.sets * 2


'''
Nutrition
'''


class MealFood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meal = db.relationship('Meal', back_populates='foods_link')
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'))
    food = db.relationship('Food', back_populates='meals_link')
    food_id = db.Column(db.Integer, db.ForeignKey('food.id'))

    # meal_food = db.Table('log_items',
    #                      db.Column('id', db.Integer, primary_key=True),
    #                      db.Column('meal_id', db.Integer, db.ForeignKey('meal.id')),
    #                      db.Column('food_id', db.Integer, db.ForeignKey('food.id'))
    #                      )


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    meals_link = db.relationship('MealFood', back_populates='food', lazy='dynamic')
    name = db.Column(db.String(50), unique=False, nullable=False, default='food item')
    protein = db.Column(db.Integer, nullable=False, default=0)
    carbs = db.Column(db.Integer, nullable=False, default=0)
    fats = db.Column(db.Integer, nullable=False, default=0)

    @property
    def calories(self):
        protein_calc = self.protein * 4
        carbs_calc = self.carbs * 4
        fats_calc = self.fats * 9
        total_calories = protein_calc + carbs_calc + fats_calc
        return total_calories


class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    foods_link = db.relationship('MealFood', back_populates='meal', lazy='dynamic')
    date = db.Column(db.Date, nullable=False)

    # foods = db.relationship('Food', secondary=MealFood.__tablename__, lazy='dynamic')

    @property
    def get_food_items(self):
        foods = []
        for item in self.foods_link:
            if item.food:
                foods.append([item.food, item.id])
            else:
                db.session.delete(item)
                db.session.commit()
        return foods

    def add_food(self, food_id):
        """
        Adds a food item to the meal.
        MealFood is appended with the food_id set to food_id passed in parameter and meal_id is set to self.id
        :param food_id: the id of the food item to add i.e. Food.id
        :return: true if food with id equal to food_id exists and was successfully added, false if not
        """
        try:
            self.foods_link.append(MealFood(food_id=food_id))
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            return False
        # meal_food = MealFood(meal_id=self.id, food_id=food_id)
        # db.session.add(meal_food)
        # db.session.commit()
        # return True

    def remove_food(self, meal_food_id):
        """
        Removes a food item from the meal.
        :param meal_food_id: the MealFood.id of entry in MealFood table associated with the food item to remove
        :return: true if food with id equal to meal_food_id exists and was successfully removed, false if not
        """
        try:
            meal_food = MealFood.query.filter_by(id=meal_food_id).first()
            db.session.delete(meal_food)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            return False
        # meal_food = MealFood.query.get(meal_food_id)
        # self.foods.remove(meal_food)
        # db.session.commit()

    @property
    def total_calories(self):
        total = 0
        for item, _ in self.get_food_items:
            total += item.calories
        return total

    @property
    def total_protein(self):
        total = 0
        for item, _ in self.get_food_items:
            total += item.protein
        return total

    @property
    def total_carbs(self):
        total = 0
        for item, _ in self.get_food_items:
            total += item.carbs
        return total

    @property
    def total_fats(self):
        total = 0
        for item, _ in self.get_food_items:
            total += item.fats
        return total
