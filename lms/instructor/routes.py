
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
            "name": student.name,
            "email": student.email,
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


@instructor.route('/course/<int:course_id>/chat')
@login_required
def course_chat(course_id):
    course = Course.query.get_or_404(course_id)

    # Ensure instructor owns the course
    if course.instructor_id != current_user.id:
        abort(403)

    # Get all messages for this course
    messages = Message.query.filter_by(course_id=course_id).order_by(Message.timestamp).all()

    # Mark messages as read for the instructor
    unread_messages = Message.query.filter_by(course_id=course_id, receiver_id=current_user.id, read=False).all()
    for msg in unread_messages:
        msg.read = True
    db.session.commit()

    return render_template('instructor/chat.html', course=course, messages=messages)


@instructor.route('/course/<int:course_id>/chat/<int:student_id>')
@login_required
def private_chat(course_id, student_id):
    course = Course.query.get_or_404(course_id)

    # Ensure instructor owns the course
    if course.instructor_id != current_user.id:
        abort(403)

    # Check if student is enrolled
    enrollment = Enrollment.query.filter_by(user_id=student_id, course_id=course_id).first()
    if not enrollment:
        abort(404)

    student = enrollment.user

    # Get private messages between instructor and this student for this course
    messages = Message.query.filter(
        Message.course_id == course_id,
        ((Message.sender_id == current_user.id) & (Message.receiver_id == student_id)) |
        ((Message.sender_id == student_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp).all()

    # Mark messages as read
    unread_messages = Message.query.filter_by(course_id=course_id, receiver_id=current_user.id, read=False).all()
    for msg in unread_messages:
        msg.read = True
    db.session.commit()

    return render_template('instructor/chat.html', course=course, messages=messages, private_student=student)


