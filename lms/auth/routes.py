# lms/auth/routes.py

from flask import render_template, redirect, url_for, flash, request, current_app, session
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
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))  # updated

    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        role = 'admin' if form.admin_code.data == current_app.config.get('ADMIN_SIGNUP_CODE') else 'student'

        user = User(name=form.name.data, email=form.email.data, password=hashed_pw, role=role)
        db.session.add(user)
        db.session.commit()

        flash(f'Account created for {form.name.data} as {role}!', 'success')
        login_user(user)
        current_app.logger.debug("login_user called for id=%s; session keys=%s", user.id, list(session.keys()))

        return redirect(url_for('main.dashboard'))  # updated

    return render_template('auth/register.html', form=form)


# ---------------------------
# Login route
# ---------------------------
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))  # updated

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            current_app.logger.debug("login_user called for id=%s; session keys=%s", user.id, list(session.keys()))
            flash('Login successful!', 'success')

            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))  # updated
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

    next_page = request.args.get('next')
    if next_page and next_page.startswith('/'):
        return redirect(next_page)

    return redirect(url_for('auth.login'))
