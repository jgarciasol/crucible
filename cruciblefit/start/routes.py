from flask import Blueprint, escape, redirect, url_for
from flask import render_template, flash, request, session
from flask_sqlalchemy import session
from flask_login import login_required, current_user
from cruciblefit.models import Food, Meal, Exercise, Workout, User, MealFood
from cruciblefit.extensions import db
from datetime import datetime, timedelta

start = Blueprint("start", __name__)

'''This is a blueprint. Used to route the pages 
We will have to update this once we add more pages, such as for viewing, adding, deleting exercises.
'''


@start.route("/")
def home():
    return render_template("home.html", user=current_user)


@start.route('/meals_overview')
@login_required
def meals_overview():
    meals = Meal.query.filter_by(user_id=current_user.id).order_by(Meal.date.desc()).all()
    meals_list = []
    for meal in meals:
        # moved the total calculations for the meal to model.py
        meals_list.append({
            'meal': meal,
            'protein': meal.total_protein,
            'fats': meal.total_fats,
            'carbs': meal.total_carbs,
            'calories': meal.total_calories
        })
    return render_template("meals_overview.html", user=current_user, meals_list=meals_list)


@start.route('/create_meal', methods=['POST'])
@login_required
# Not sure if we could use this
def create_meal():
    date = request.form.get('date')
    meal = Meal(date=datetime.strptime(date, '%Y-%m-%d'), user_id=current_user.id)
    db.session.add(meal)
    db.session.commit()
    return redirect(url_for('start.edit_view_meal', meal_id=meal.id))


@start.route("/edit_view_meal/<int:meal_id>")
@login_required
def edit_view_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    macros_totals = {
        'protein': meal.total_protein,
        'carbs': meal.total_carbs,
        'fats': meal.total_fats,
        'calories': meal.total_calories
    }
    # used to calculate the nutrients for specific log date
    foods = Food.query.filter((Food.user_id == current_user.id) | (Food.user_id == None)).all()
    return render_template("edit_view_meal.html", user=current_user, foods=foods, meal=meal, totals=macros_totals)


@start.route('/add_food_to_meal/<int:meal_id>', methods=['POST'])
@login_required
def add_food_to_meal(meal_id):
    chosen_food = request.form.get('food-select')
    meal = Meal.query.get_or_404(meal_id)
    #meal.add_food(int(chosen_food)) #causes a crash NoneType in /edit_view_meal/2
    meal.add_food(chosen_food)
    return redirect(url_for('start.edit_view_meal', meal_id=meal_id))


@start.route('/remove_food_from_meal/<int:meal_id>/<int:meal_food_id>')
@login_required
def remove_food_from_meal(meal_id, meal_food_id):
    meal = Meal.query.get(meal_id)
    meal.remove_food(meal_food_id)
    db.session.commit()
    return redirect(url_for('start.edit_view_meal', meal_id=meal_id))


@start.route("/food_items_overview")
@login_required
def food_items_overview():
    foods = Food.query.filter((Food.user_id == current_user.id) | (Food.user_id == None)).all()
    return render_template("add_food.html", user=current_user, foods=foods, food=None)


@start.route("/food_items_overview", methods=['POST'])
@login_required
def add_food():
    food_name = request.form.get('food-name')
    proteins = request.form.get('protein')
    carbs = request.form.get('carbohydrates')
    fats = request.form.get('fat')

    food_id = request.form.get('food-id')

    # being able to edit and update values
    if food_id:
        # get_or_404 if id does not exist
        food = Food.query.get_or_404(food_id)
        food.name = food_name
        food.protein = proteins
        food.carbs = carbs
        food.fats = fats

    else:
        # creates new food if id does not exist
        new_food = Food(name=food_name, protein=proteins, carbs=carbs,
                        fats=fats, user_id=current_user.id)

        db.session.add(new_food)  # adds new food to db

    db.session.commit()
    return redirect(url_for('start.food_items_overview'))


@start.route('/delete_food/<int:food_id>')
@login_required
def delete_food(food_id):
    food = Food.query.get_or_404(food_id)
    db.session.delete(food)

    db.session.commit()

    return redirect(url_for('start.food_items_overview'))


@start.route('/edit_food_item/<int:food_id>')
@login_required
def edit_food_item(food_id):
    food = Food.query.get_or_404(food_id)
    foods = Food.query.filter((Food.user_id == current_user.id) | (Food.user_id == None)).all()
    return render_template('add_food.html', user=current_user, food=food, foods=foods)


@start.route('/fitness')
@login_required
def fitness_overview():
    workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date.desc(),
                                                                         Workout.start_time.desc()).all()
    # workouts_list = []
    # for workout in workouts:
    #     # moved the total calculations for the meal to model.py
    #     workouts_list.append({
    #         'workout': workout,
    #         'cals_burned': workout.total_calories
    #     })
    return render_template("fitness_overview.html", user=current_user, workouts_list=workouts)


# @start.route('/fitness', methods=['POST'])
# @login_required
# def add_prior_workout():
#     time = datetime.now() + timedelta(hours=1)
#     workout = Workout(date=datetime.now().date(), start_time=datetime.now().time(), end_time=time.time(),
#                       user_id=current_user.id)
#     db.session.add(workout)
#     db.session.commit()
#     return redirect(url_for('start.view_workout_record', workout_id=workout.id))


@start.route('/view_workout_record/<int:workout_id>')
@login_required
def view_workout_record(workout_id):
    if workout_id == 0:
        time = datetime.now() + timedelta(hours=1)
        workout = Workout(date=datetime.now().date(), start_time=datetime.now().time(), end_time=time.time(),
                          user_id=current_user.id)
        db.session.add(workout)

        db.session.commit()
    else:
        workout = Workout.query.get_or_404(workout_id)
    workout_info = {
        'workout': workout,
        'id': workout.id,
        'date': workout.date,
        'start_time': workout.start_time,
        'end_time': workout.end_time,
        'workout_notes': workout.workout_notes
    }
    return render_template("view_workout_record.html", user=current_user, workout_id=workout.id,
                           workout_info=workout_info)


@start.route('/edit_workout_record/<int:workout_id>', methods=['POST'])
@login_required
def edit_workout_record(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    workout.start_time = request.form.get('start-time')
    workout.end_time = request.form.get('end-time')
    workout.date = request.form.get('date')
    workout.notes = request.form.get('notes')
    db.session.commit()
    return redirect(url_for('start.view_workout_record', workout_id=workout.id))


@start.route('/remove_food_from_meal/<int:workout_exercise_id>/<int:workout_id>')
@login_required
def remove_exercise_from_workout(workout_exercise_id, workout_id):
    workout = Meal.query.get(workout_id)
    workout.remove_food(workout_exercise_id)
    db.session.commit()
    return redirect(url_for('start.view_workout_record', workout=workout))


@start.route('/pre_workout')
@login_required
def pre_workout():
    return render_template('pre_workout.html', user=current_user)


@start.route("/add_ex", methods=['POST'])
@login_required
def add_ex():
    ex_name = request.form.get('exercise-name')
    ex_type = request.form.get('type')
    ex_reps = request.form.get('reps')
    ex_sets = request.form.get('sets')
    # if workout_id:
    #     # get_or_404 if id does not exist
    #     exercise = Exercise.query.get_or_404(workout_id)
    #     exercise.name = ex_name
    #     exercise.type = ex_type
    #     exercise.reps = ex_reps
    #     exercise.sets = ex_sets
    # else:
    #     new_workout = Workout(name=ex_name, type=ex_type, reps=ex_reps,
    #                           sets=ex_sets)
    #
    #     db.session.add(new_workout)
    #
    # db.session.commit()
    return redirect(url_for('start.add_ex'))
