# lms/instructor/routes.py

from flask import Blueprint, render_template, abort
from flask_login import current_user, login_required
from lms.models import Course, Enrollment, User
from . import instructor
from lms.models.lesson_completion import LessonCompletion   
from lms.main.routes import time_ago_in_words  


@instructor.before_request
def restrict_to_instructors():
    if not current_user.is_authenticated or current_user.role != 'instructor':
        abort(403)

@instructor.route('/dashboard')
@login_required
def dashboard():
    courses = Course.query.filter_by(instructor_id=current_user.id).all()
    return render_template('instructor/dashboard.html', courses=courses)


@instructor.route('/course/<int:course_id>/students')
@login_required
def course_students(course_id):
    course = Course.query.get_or_404(course_id)

    # Ensure instructor owns the course
    if course.instructor_id != current_user.id:
        abort(403)

    enrollments = course.enrollments.all()
    students_data = []

    for enrollment in enrollments:
        student = enrollment.user

        # --- Get Progress Stats For Each Student ---
        courses_enrolled = student.user_enrollments.count()
        lessons_watched = student.lesson_completions.count()
        courses_completed = student.user_enrollments.filter_by(completed=True).count()

        # Last active time
        latest_completion = student.lesson_completions.order_by(
            LessonCompletion.completed_at.desc()
        ).first()

        last_active = time_ago_in_words(latest_completion.completed_at) if latest_completion else "New user"

        students_data.append({
            "id": student.id,  # ← NEW: Include student ID for messaging
            "name": student.name,
            "email": student.email,
            "status": "active",  # ← NEW: Add status field (you can customize this logic)
            "courses_enrolled": courses_enrolled,
            "lessons_watched": lessons_watched,
            "courses_completed": courses_completed,
            "last_active": last_active
        })

    return render_template(
        'instructor/course_students.html',
        course=course,
        students=students_data
    )