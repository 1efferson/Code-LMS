
from flask import Blueprint, render_template, abort
from flask_login import current_user, login_required
from lms.models import Course, Enrollment, User
from . import instructor


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

    # Get enrollments for this course
    enrollments = course.enrollments.all()

    # Get students via backref (clean!)
    students = [enrollment.user for enrollment in enrollments]

    return render_template(
        'instructor/course_students.html',
        course=course,
        students=students
    )

