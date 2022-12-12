from flask import Blueprint, escape, redirect, url_for
from flask import render_template, flash, request, session
from flask_sqlalchemy import session
from flask_login import login_user, login_required, logout_user, current_user
from cruciblefit.models import Food, Meal, Exercise, Workout
from cruciblefit.extensions import db
from datetime import datetime

start = Blueprint("start", __name__)

'''This is a blueprint. Used to route the pages 
We will have to update this once we add more pages, such as for viewing, adding, deleting exercises.
'''


@start.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("start.meals_overview"))
    return redirect(url_for("auth.login"))


@start.route('/meals_overview')
@login_required
def meals_overview():
    meals = Meal.query.filter_by(user_id=current_user.id).order_by(Meal.date.desc()).all()
    log_dates = []
    # outer loop, loops through each meal date in the database
    for meal in meals:
        protein = 0
        carbs = 0
        fats = 0
        calories = 0
        # loop through each food in the meal dates to update macro values
        for food in meal.foods:
            protein += food.protein
            carbs += food.carbs
            fats += food.fats
            calories += food.calories
        # append to dictionary that gets send to meals_overview.html

        log_dates.append({
            'log_date': meal,
            'protein': protein,
            'fats': fats,
            'carbs': carbs,
            'calories': calories
        })
    return render_template("meals_overview.html", user=current_user, log_dates=log_dates)


@start.route('/create_meal', methods=['POST'])
@login_required
# Not sure if we could use this
def create_meal():
    date = request.form.get('date')
    log = Meal(date=datetime.strptime(date, '%Y-%m-%d'), user_id=current_user.id)
    db.session.add(log)
    db.session.commit()
    return redirect(url_for('start.edit_view_meal', log_id=log.id))


@start.route("/food_items_overview")
@login_required
def food_items_overview():
    foods = Food.query.all()
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
    if (food_id):
        # get_or_404 if id does not exist
        food = Food.query.get_or_404(food_id)
        food.name = food_name
        food.protein = proteins
        food.carbs = carbs
        food.fats = fats

    else:
        # creates new food if id does not exist
        new_food = Food(name=food_name, protein=proteins, carbs=carbs,
                        fats=fats)

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
    foods = Food.query.all()
    return render_template('add_food.html', user=current_user, food=food, foods=foods)


@start.route("/edit_view_meal/<int:log_id>")
@login_required
def edit_view_meal(log_id):
    logs = Meal.query.get_or_404(log_id)
    foods = Food.query.all()

    macros_totals = {
        'protein': 0,
        'carbs': 0,
        'fats': 0,
        'calories': 0
    }

    # used to calculate the nutrients for specific log date
    for food in logs.foods:
        macros_totals['protein'] += food.protein
        macros_totals['carbs'] += food.carbs
        macros_totals['fats'] += food.fats
        macros_totals['calories'] += food.calories

    return render_template("edit_view_meal.html", user=current_user, foods=foods, meal=logs, totals=macros_totals)


@start.route('/add_food_to_meal/<int:log_id>', methods=['POST'])
@login_required
def add_food_to_meal(log_id):
    logs = Meal.query.get_or_404(log_id)
    chosen_food = request.form.get('food-select')
    food = Food.query.get(int(chosen_food))
    logs.foods.append(food)
    db.session.commit()
    return redirect(url_for('start.edit_view_meal', log_id=log_id))


# remove food from particular date view
@start.route('/remove_food_from_meal/<int:log_id>/<int:food_id>')
@login_required
def remove_food_from_meal(log_id, food_id):
    log = Meal.query.get(log_id)
    food = Food.query.get(food_id)

    log.foods.remove(food)
    db.session.commit()

    return redirect(url_for('start.edit_view_meal', log_id=log_id))


@start.route('/fitness')
@login_required
def fitness_view():
    return render_template('fitness_view.html', user=current_user)


@start.route("/add_ex", methods=['POST'])
@login_required
def add_ex():
    ex_name = request.form.get('exercise-name')
    ex_type = request.form.get('What type of activity')
    ex_reps = request.form.get('What is the number of reps done')
    ex_sets = request.form.get('What was the number of sets done')
    workout_id = request.form.get('workout_id')
    if workout_id:
        # get_or_404 if id does not exist
        exercise = Exercise.query.get_or_404(workout_id)
        exercise.name = ex_name
        exercise.type = ex_type
        exercise.reps = ex_reps
        exercise.sets = ex_sets
    else:
        new_workout = Workout(name=ex_name, type=ex_type, reps=ex_reps,
                              sets=ex_sets)

        db.session.add(new_workout)

    db.session.commit()
    return redirect(url_for('start.add_ex'))
