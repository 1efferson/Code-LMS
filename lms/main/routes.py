
# lms/main/routes.py
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from lms.models import Enrollment

from . import main  # import the blueprint from __init__.py

@main.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/home.html')

@main.route('/dashboard')
@login_required
def dashboard():
    user = current_user
    # Get course objects the user is enrolled in
    enrollments = Enrollment.query.filter_by(user_id=user.id).all()
    courses = [enrollment.course for enrollment in enrollments if enrollment.course]

    return render_template(
        'main/dashboard.html',
        user=user,
        courses=courses,
    )

@main.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html', user=current_user)
