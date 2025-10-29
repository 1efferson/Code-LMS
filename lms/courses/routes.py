# lms/courses/routes.py

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from lms import db
from lms.models.course import Course
from lms.models.enrollment import Enrollment
from . import courses  
from lms.models.module import Module
from lms.models.lesson import Lesson
from lms.models.lesson_completion import LessonCompletion 
from sqlalchemy.orm import joinedload
from sqlalchemy import select # Added select for explicit queries

# -------------------------------
#  Course Catalog
# -------------------------------
@courses.route('/')  
@login_required
def index():
    """Display all published courses."""
    # Note: If Course.query is a simple query, this is fine, but using db.session.execute is preferred with joinedload
    courses_list = Course.query.filter_by(published=True).order_by(Course.created_at.desc()).all()
    return render_template('courses/courses_catalog.html', courses=courses_list)


# -------------------------------
#  Course Detail Page
# -------------------------------
@courses.route('/<slug>')
@login_required
def course_detail(slug):
    """Display details for a single course, eagerly loading the instructor (Fix for 'Taught By')."""
    
    # FIX: Use db.select() and joinedload() to fetch the course and instructor in one query
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
#  Enroll in a Course
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
#  Course Lessons Page (Initial redirection to first lesson)
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
#  Specific Lesson Player (Combined Logic)
# -------------------------------
@courses.route('/<course_slug>/lessons/<lesson_slug>', methods=['GET', 'POST'])
@login_required
def course_lesson(course_slug, lesson_slug):
    """
    Shows the course player with a specific lesson active.
    """
    # FIX: Use db.select() and joinedload() to fetch the course and instructor
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
        is_complete=is_complete
    )


# -------------------------------
#  Mark Lesson as Complete (MISSING ROUTE ADDED)
# -------------------------------
@courses.route('/<lesson_slug>/complete', methods=['POST'])
@login_required
def mark_lesson_complete(lesson_slug):
    """Marks a specific lesson as completed by the current user."""
    
    lesson = Lesson.query.filter_by(slug=lesson_slug).first_or_404()
    
    existing_completion = LessonCompletion.query.filter_by(
        user_id=current_user.id,
        lesson_id=lesson.id
    ).first()

    if existing_completion:
        flash('This lesson is already marked as complete.', 'info')
    else:
        completion = LessonCompletion(
            user_id=current_user.id, 
            lesson_id=lesson.id
        )
        db.session.add(completion)
        db.session.commit()
        flash('Lesson marked as complete!', 'success')
        
    return redirect(url_for('courses.course_lesson', 
                            course_slug=lesson.module.course.slug, 
                            lesson_slug=lesson_slug))


# -------------------------------
#  Unmark Lesson as Complete
# -------------------------------
@courses.route('/<lesson_slug>/unmark', methods=['POST'])
@login_required
def unmark_lesson_complete(lesson_slug):
    """Removes the lesson completion record for the current user."""
    
    lesson = Lesson.query.filter_by(slug=lesson_slug).first_or_404()
    
    completion = LessonCompletion.query.filter_by(
        user_id=current_user.id,
        lesson_id=lesson.id
    ).first()

    if completion:
        db.session.delete(completion)
        db.session.commit()
        flash('Lesson completion status removed.', 'warning')
    else:
        flash('This lesson was not marked as complete.', 'info')
        
    return redirect(url_for('courses.course_lesson', 
                            course_slug=lesson.module.course.slug, 
                            lesson_slug=lesson_slug))