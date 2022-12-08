from flask import Blueprint, escape, redirect, url_for
from flask import render_template, flash, request, session
from flask_sqlalchemy import session
from flask_login import login_user, login_required, logout_user, current_user
from cruciblefit.models import Food, Log
from cruciblefit.extensions import db
from datetime import datetime


start = Blueprint("start", __name__)

'''This is a blueprint. Used to route the pages 
We will have to update this once we add more pages, such as for viewing, adding, deleting exercises.
'''


@start.route('/')
@login_required
def index():
    logs = Log.query.order_by(Log.date.desc()).all()
    log_dates = []
    #outer loop, loops through each log date in the database
    for log in logs:
        protein = 0
        carbs = 0
        fats = 0
        calories = 0
        #loop through each food in the log dates to update macro values
        for food in log.foods:
            protein += food.protein
            carbs += food.carbs
            fats += food.fats
            calories += food.calories
        #append to dictionary that gets send to index.html
        log_dates.append({
            'log_date': log, 
            'protein': protein,
            'fats': fats,
            'carbs': carbs,
            'calories': calories
            })
    return render_template("index.html", user=current_user, log_dates=log_dates)


@start.route('/create_log', methods = ['POST'])
@login_required
##Not sure if we could use this
def create_log():
    date = request.form.get('date')
    log = Log(date = datetime.strptime(date, '%Y-%m-%d'))
    db.session.add(log)
    db.session.commit()
    return redirect(url_for('start.view', log_id = log.id))

@start.route("/add")
@login_required
def add():
    foods = Food.query.all()
    return render_template("add.html", user=current_user, foods=foods, food = None)

@start.route("/add", methods = ['POST'])
@login_required
def add_food():
    food_name = request.form.get('food-name')
    proteins = request.form.get('protein')
    carbs = request.form.get('carbohydrates')
    fats = request.form.get('fat')

    food_id = request.form.get('food-id')

    #being able to edit and update values
    if(food_id):
        #get_or_404 if id does not exist
        food = Food.query.get_or_404(food_id)
        food.name = food_name
        food.protein = proteins
        food.carbs = carbs
        food.fats = fats
    
    else:
        #creates new food if id does not exist
        new_food = Food(name=food_name, protein = proteins, carbs = carbs,
        fats = fats)

        db.session.add(new_food) #adds new food to db

    db.session.commit() 
    return redirect(url_for('start.add'))

@start.route('/delete_food/<int:food_id>')
@login_required
def delete_food(food_id):
    food = Food.query.get_or_404(food_id)
    db.session.delete(food)
    db.session.commit()

    return redirect(url_for('start.add'))

@start.route('/edit_food/<int:food_id>')
@login_required
def edit_food(food_id):
    food = Food.query.get_or_404(food_id)
    foods = Food.query.all()
    return render_template('add.html', food = food, foods = foods)


@start.route("/view/<int:log_id>")
@login_required
def view(log_id):
    logs = Log.query.get_or_404(log_id)
    foods = Food.query.all()
    
    macros_totals= {
        'protein': 0,
        'carbs' : 0,
        'fats' : 0,
        'calories': 0
    }

    #used to calculate the nutrients for specific log date
    for food in logs.foods:
        macros_totals['protein'] += food.protein
        macros_totals['carbs'] += food.carbs
        macros_totals['fats'] += food.fats
        macros_totals['calories'] +=food.calories

    return render_template("view.html", user=current_user, foods = foods, log=logs, totals=macros_totals)


@start.route('/add_food_to_log/<int:log_id>', methods = ['POST'])
@login_required
def add_food_to_log(log_id):
    logs = Log.query.get_or_404(log_id)
    chosen_food = request.form.get('food-select')
    food = Food.query.get(int(chosen_food))
    logs.foods.append(food)
    db.session.commit()
    return redirect(url_for('start.view', log_id=log_id))


#remove food from particular date view
@start.route('/remove_food_from_log_date/<int:log_id>/<int:food_id>')
@login_required
def remove_food_from_log_date(log_id,food_id):

    log = Log.query.get(log_id)
    food = Food.query.get(food_id)

    log.foods.remove(food)
    db.session.commit()


    return redirect(url_for('start.view', log_id=log_id))