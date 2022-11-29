from flask import Blueprint, render_template

start = Blueprint("start", __name__)

'''This is a blueprint. Used to route the pages 
We will have to update this once we add more pages, such as for viewing, adding, deleting exercises.
'''

@start.route('/')
def index():
    return render_template("index.html")

@start.route("/add")
def add():
    return render_template("add.html")

@start.route("/view")
def view():
    return render_template("view.html")