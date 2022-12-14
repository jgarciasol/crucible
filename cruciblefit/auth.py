from datetime import datetime

from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('start.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        new_email = request.form.get('email')
        new_first_name = request.form.get('firstName')
        new_weight = request.form.get('weight')
        new_height = request.form.get('height')
        new_dob = request.form.get('dob')
        new_password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        try:
            new_dob = datetime.strptime(new_dob, '%Y-%m-%d')
        except ValueError as exception:
            flash('Try inserting correct date', category='error')
        user = User.query.filter_by(email=new_email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(new_email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(new_first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif new_password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(new_password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=new_email, first_name=new_first_name, password=generate_password_hash(
                new_password1, method='sha256'), weight=new_weight, height=new_height, dob=new_dob)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('start.home'))

    return render_template("sign_up.html", user=current_user)
