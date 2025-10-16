
# lms/main/routes.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def home():
    return render_template('main/home.html')

@main.route('/dashboard')
@login_required
def dashboard():
    # Temporary mock data
    courses = [
        {"title": "Tkinter Basics", "desc": "Learn to build GUIs in Python.", "url": "#"},
        {"title": "Python Introductory Course", "desc": "Core Python fundamentals.", "url": "#"},
        {"title": "Python Turtle", "desc": "Visual programming with Turtle graphics.", "url": "#"},
    ]

    attendance = {"attended": 8, "total": 10}

    events = [
        {"title": "Python Bootcamp", "date": "Oct 10, 2025"},
        {"title": "Code Review Workshop", "date": "Oct 15, 2025"},
    ]

    news = [
        {"title": "New Library Resources", "summary": "More e-books added to the Python collection."},
        {"title": "Upcoming Hackathon", "summary": "Participate in the Cellusys coding challenge."},
    ]

    return render_template(
        'dashboard.html',
        user=current_user,
        courses=courses,
        attendance=attendance,
        events=events,
        news=news, hide_navbar=True
    )
