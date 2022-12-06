from flask import Blueprint, escape
from flask import render_template, flash, request, session
from flask_sqlalchemy import session
from flask_login import login_user, login_required, logout_user, current_user

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
    return render_template("add.html", user=current_user)


@start.route("/view")
@login_required
def view():
    return render_template("view.html", user=current_user)
