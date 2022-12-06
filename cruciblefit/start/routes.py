import gc

from django.db import connection
from flask import Blueprint, escape
from flask import render_template, flash, request, session
from flask_sqlalchemy import session
from passlib.hash import sha256_crypt
from wtforms import Form, BooleanField, StringField, PasswordField, validators


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=20)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('new password', [validators.data_required(),
                                              validators.equal_to('confirm', message='Passwords must match')
                                              ])
    confirm = PasswordField('Repeat Password')
    accept_terms_of_service = BooleanField('I accept the Terms of Service and Privacy Policy')


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


@start.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return render_template("index.html")
    return render_template('login.html', error=error)


@start.route('/register', methods=['GET', 'POST'])
def register():
    try:
        form = RegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrpyt((str(form.password.data)))
            c, conn = connection()
            x = c.execute("SELECT * FORM users WHERE username = (%s)"), (escape(username))
            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template('registration.html', form=form)
            else:
                c.execute("Insert INTO users (username, password, email) VALUES (%s, %s, %s)"),
                (escape(username), escape(password), escape(email))
                conn.commit()
                flash("Thanks for registering")
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] = True
                session['username'] = True

                return render_template("index.html")
        return render_template("registration.html")
    except Exception as e:
        return str(e)

