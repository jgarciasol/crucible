from flask import Blueprint, escape, redirect, url_for
from flask import render_template, flash, request, session
from flask_sqlalchemy import session
from flask_login import login_user, login_required, logout_user, current_user
from cruciblefit.models import Food
from cruciblefit.extensions import db
start = Blueprint("start", __name__)

'''This is a blueprint. Used to route the pages 
We will have to update this once we add more pages, such as for viewing, adding, deleting exercises.
'''


@start.route('/')
@login_required
def index():
    return render_template("index.html", user=current_user)


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
        food = Food.query.get(food_id)
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
    food = Food.query.get(food_id)
    db.session.delete(food)
    db.session.commit()

    return redirect(url_for('start.add'))

@start.route('/edit_food/<int:food_id>')
@login_required
def edit_food(food_id):
    food = Food.query.get(food_id)
    foods = Food.query.all()
    return render_template('add.html', food = food, foods = foods)


@start.route("/view")
@login_required
def view():
    return render_template("view.html", user=current_user)
