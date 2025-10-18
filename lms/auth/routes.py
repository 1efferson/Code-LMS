# lms/auth/routes.py

from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from lms import db, bcrypt
from lms.models import User
from .forms import RegisterForm, LoginForm
from . import auth


# ---------------------------
# Registration route
# ---------------------------
@auth.route('/register', methods=['GET', 'POST'])
def register():
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        # Hash password
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # Determine role using admin signup code
        role = 'admin' if form.admin_code.data == current_app.config.get('ADMIN_SIGNUP_CODE') else 'student'

        # Create new user
        user = User(name=form.name.data, email=form.email.data, password=hashed_pw, role=role)
        db.session.add(user)
        db.session.commit()

        flash(f'Account created for {form.name.data} as {role}!', 'success')
        login_user(user)
        return redirect(url_for('main.dashboard'))

    return render_template('auth/register.html', form=form)


# ---------------------------
# Login route
# ---------------------------
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))  # already logged in? go to dashboard

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')

            # Redirect to next page if it exists, otherwise dashboard
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html', form=form)


# ---------------------------
# Logout route
# ---------------------------
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')

    # Optional: support for ?next= redirect if added later
    next_page = request.args.get('next')
    if next_page and next_page.startswith('/'):
        return redirect(next_page)

    return redirect(url_for('auth.login'))
