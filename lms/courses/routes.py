# lms/courses/routes.py

from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from lms import db
from lms.models.course import Course
from lms.models.enrollment import Enrollment
from lms.models.message import Message
from . import courses
from lms.models.module import Module
from lms.models.lesson import Lesson
from lms.models.lesson_completion import LessonCompletion
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from datetime import datetime
import json

# -------------------------------
#  Course Catalog
# -------------------------------
@courses.route('/') 
@login_required
def index():
    """Display all published courses."""
    stmt = (
        select(Course)
        .options(joinedload(Course.instructor))
        .where(Course.published == True)
        .order_by(Course.created_at.desc())
    )

    courses_list = db.session.execute(stmt).scalars().all()

    # --- START: Load Lottie Data Directly from File ---
    lottie_data = None
    try:
        # Construct the full path to the JSON file relative to the application's root (lms folder)
        # File is expected at: lms/courses/static/lottie/streak.json
        json_path = current_app.root_path + '/courses/static/lottie/streak.json'
        with open(json_path, 'r') as f:
            lottie_data = json.load(f)
    except FileNotFoundError:
        # Log error if file not found
        print(f"Lottie file not found at: {json_path}") 
    except Exception as e:
        # Log other potential loading errors
        print(f"Error loading Lottie JSON: {e}")
    # --- END: Load Lottie Data ---

    return render_template(
        'courses/courses_catalog.html', 
        courses=courses_list, 
        today=datetime.utcnow(),
        lottie_animation=lottie_data # <--- PASSING THE DATA
    )


# -------------------------------
#  Course Detail Page
# -------------------------------
@courses.route('/<slug>')
@login_required
def course_detail(slug):
    """Display details for a single course, eagerly loading the instructor (Fix for 'Taught By')."""
    
    # Use db.select() and joinedload() to fetch the course and instructor in one query
    course = db.session.execute(
        select(Course)
        .filter_by(slug=slug, published=True)
        .options(joinedload(Course.instructor))
    ).scalar_one_or_none()

    if not course:
        return redirect(url_for('courses.index')) # Redirect if course not found or not published
        
    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course.id).first()

    return render_template(
        'courses/course_details.html',
        course=course,
        is_enrolled=bool(enrollment)
    )


# -------------------------------
#  Enroll in a Course
# -------------------------------
@courses.route('/<slug>/enroll', methods=['POST'])
@login_required
def enroll(slug):
    """Enroll the current user in a course."""
    course = Course.query.filter_by(slug=slug, published=True).first_or_404()

    # Check if already enrolled
    existing = Enrollment.query.filter_by(user_id=current_user.id, course_id=course.id).first()
    if existing:
        flash('You are already enrolled in this course.', 'info')
        return redirect(url_for('courses.course_detail', slug=slug))

    # Create new enrollment record
    enrollment = Enrollment(user_id=current_user.id, course_id=course.id)
    db.session.add(enrollment)
    db.session.commit()

    flash('You have successfully enrolled in this course!', 'success')
    return redirect(url_for('courses.course_lessons', slug=slug))


# -------------------------------
#  Course Lessons Page (Initial redirection to first lesson)
# -------------------------------
@courses.route('/<slug>/lessons')
@login_required
def course_lessons(slug):
    """
    Shows the course player. Defaults to the very first lesson.
    """
    course = Course.query.filter_by(slug=slug, published=True).first_or_404()
    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course.id).first()

    if not enrollment:
        flash('You must enroll in this course to view the lessons.', 'warning')
        return redirect(url_for('courses.course_detail', slug=slug))

    # Find the first module and the first lesson to play by default
    first_module = course.modules.order_by(Module.order).first()
    first_lesson = None
    if first_module:
        first_lesson = first_module.lessons.order_by(Lesson.order).first() # Use order_by(Lesson.order) if possible
    
    # If there's a first lesson, redirect to the specific lesson player route
    if first_lesson:
        return redirect(url_for('courses.course_lesson', 
                                 course_slug=course.slug, 
                                 lesson_slug=first_lesson.slug))

    # If there are no lessons at all yet, show a placeholder page
    flash('Lessons are coming soon for this course!', 'info')
    return render_template(
        'courses/course_lessons.html',
        course=course,
        current_lesson=None,  # No lesson to play
        modules=course.modules.order_by(Module.order).all() # Pass modules for sidebar
    )


# -------------------------------
#  Specific Lesson Player (Combined Logic)
# -------------------------------
@courses.route('/<course_slug>/lessons/<lesson_slug>', methods=['GET', 'POST'])
@login_required
def course_lesson(course_slug, lesson_slug):
    """
    Shows the course player with a specific lesson active.
    """
    # Use db.select() and joinedload() to fetch the course and instructor
    course = db.session.execute(
        select(Course)
        .filter_by(slug=course_slug, published=True)
        .options(joinedload(Course.instructor))
    ).scalar_one_or_none()
    
    if not course:
        return redirect(url_for('courses.index'))

    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course.id).first()

    if not enrollment:
        flash('You must enroll in this course to view the lessons.', 'warning')
        return redirect(url_for('courses.course_detail', slug=course.slug))

    # Find the specific lesson
    lesson = Lesson.query.filter_by(slug=lesson_slug).first_or_404()
    
    # Check if the user has completed this lesson
    is_complete = LessonCompletion.query.filter_by(
        user_id=current_user.id, 
        lesson_id=lesson.id
    ).first() is not None
    
    # Get all modules for the sidebar
    modules = course.modules.order_by(Module.order).all()

    return render_template(
        'courses/course_lesson.html',
        course=course,
        current_lesson=lesson,
        modules=modules,
        is_complete=is_complete,
        enrollment=enrollment
    )

# -------------------------------
#  Mark Lesson as Complete
# -------------------------------
@courses.route('/<lesson_slug>/complete', methods=['POST'])
@login_required
def mark_lesson_complete(lesson_slug):
    lesson = Lesson.query.filter_by(slug=lesson_slug).first_or_404()

    # Check if already marked
    completion = LessonCompletion.query.filter_by(
        user_id=current_user.id,
        lesson_id=lesson.id
    ).first()

    if completion:
        flash('This lesson is already marked as complete.', 'info')
    else:
        completion = LessonCompletion(user_id=current_user.id, lesson_id=lesson.id)
        db.session.add(completion)
        db.session.commit()
        flash('Lesson marked as complete!', 'success')

    # Update enrollment after marking completion
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=lesson.module.course.id
    ).first()
    if enrollment:
        enrollment.check_and_update_completion()

    return redirect(url_for(
        'courses.course_lesson',
        course_slug=lesson.module.course.slug,
        lesson_slug=lesson.slug
    ))

# -------------------------------
#  Course Chat
# -------------------------------
@courses.route('/<course_slug>/chat')
@login_required
def course_chat(course_slug):
    course = Course.query.filter_by(slug=course_slug, published=True).first_or_404()

    # Check if user is enrolled or is the instructor
    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course.id).first()
    if not enrollment and course.instructor_id != current_user.id:
        flash('You must be enrolled in this course or be the instructor to access the chat.', 'warning')
        return redirect(url_for('courses.course_detail', slug=course_slug))

    # Get messages for the current user (including private messages)
    messages = Message.query.filter(
        Message.course_id == course.id,
        ((Message.sender_id == current_user.id) | (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp).all()

    # Mark messages as read for the current user
    unread_messages = Message.query.filter_by(course_id=course.id, receiver_id=current_user.id, read=False).all()
    for msg in unread_messages:
        msg.read = True
    db.session.commit()

    return render_template('courses/chat.html', course=course, messages=messages)


# -------------------------------
#  Unmark Lesson as Complete
# -------------------------------
@courses.route('/<lesson_slug>/unmark', methods=['POST'])
@login_required
def unmark_lesson_complete(lesson_slug):
    lesson = Lesson.query.filter_by(slug=lesson_slug).first_or_404()

    completion = LessonCompletion.query.filter_by(
        user_id=current_user.id,
        lesson_id=lesson.id
    ).first()

    if completion:
        db.session.delete(completion)
        db.session.commit()
        flash('Lesson completion status removed.', 'warning')

    # Recalculate enrollment status after unmarking
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=lesson.module.course.id
    ).first()
    if enrollment:
        enrollment.check_and_update_completion()

    return redirect(url_for(
        'courses.course_lesson',
        course_slug=lesson.module.course.slug,
        lesson_slug=lesson.slug
    ))