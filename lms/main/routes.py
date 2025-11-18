from flask import render_template, redirect, url_for, flash, request,session
from flask_login import login_required, current_user
from datetime import datetime, timezone
from lms import db

from lms.models.enrollment import Enrollment
from lms.models.lesson_completion import LessonCompletion
from lms.models.course import Course
from lms.models.lesson import Lesson
from . import main


# --------------------------------------------------------
# HELPER FUNCTION: Calculates "time ago" in words
# --------------------------------------------------------
def time_ago_in_words(dt):
    """Returns a human-readable 'time ago' string."""
    if not dt:
        return 'N/A'

    # Handle naive datetimes
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        dt = dt.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    diff = now - dt
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif seconds < 2592000:  # 30 days
        days = seconds // 86400
        return f"{days} day{'s' if days > 1 else ''} ago"
    else:
        return dt.strftime('%b %d, %Y')


# --------------------------------------------------------
# ROUTES
# --------------------------------------------------------
@main.route('/', endpoint='home')
def index():
    return render_template('main/home.html')


@main.route('/dashboard')
@login_required
def dashboard():
    """Displays the student's enrolled courses and progress."""

    # --- Enrollments ---
    enrollments = (
        Enrollment.query
        .filter_by(user_id=current_user.id)
        .join(Course)
        .order_by(Enrollment.date_enrolled.desc())
        .all()
    )

    # --- Course Data with Progress ---
    courses_data = []
    for e in enrollments:
        course = e.course
        total_lessons = sum(module.lessons.count() for module in course.modules)

        completed_lessons = (
            LessonCompletion.query
            .join(Lesson)
            .filter(
                LessonCompletion.user_id == current_user.id,
                Lesson.module_id.in_([m.id for m in course.modules])
            )
            .count()
        )

        progress = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0

        courses_data.append({
            "title": course.title,
            "slug": course.slug,
            "description": course.description[:120] + "..." if course.description else "No description available.",
            "progress": progress,
            "completed": e.completed,
            "date_enrolled": time_ago_in_words(e.date_enrolled),
            "url": url_for("courses.course_detail", slug=course.slug)
        })

    # --- Dashboard Metrics ---
    courses_count = current_user.user_enrollments.count()  # total enrolled
    courses_completed = current_user.user_enrollments.filter_by(completed=True).count()  # finished
    active_courses = current_user.user_enrollments.filter_by(completed=False).count()  # in progress

    overall_progress = (
        int(sum(c["progress"] for c in courses_data) / len(courses_data))
        if courses_data else 0
    )

    # --- Unread Messages Count ---
    unread_messages = Message.query.filter_by(receiver_id=current_user.id, read=False).count()

    # --- Example placeholders for events and news ---
    events = [
        {"title": "Group Study Session", "date": "Nov 5, 2025"},
        {"title": "New Course Release", "date": "Nov 10, 2025"},
    ]

    news = [
        {"title": "System Update Completed", "summary": "The LMS platform has been updated with performance improvements."},
        {"title": "New Quiz Features", "summary": "You can now track quiz attempts and scores in your dashboard."}
    ]

    return render_template(
        "main/dashboard.html",
        user=current_user,
        courses=courses_data,
        courses_count=courses_count,
        courses_completed=courses_completed,
        active_courses=active_courses,
        overall_progress=overall_progress,
        events=events,
        news=news
    )


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Displays and updates the user's profile information."""
    
    # --- 1. LAST ACTIVE CALCULATION ---
    latest_completion = current_user.lesson_completions.order_by(
        LessonCompletion.completed_at.desc()
    ).first()

    last_active_datetime = latest_completion.completed_at if latest_completion else None
    last_active_string = time_ago_in_words(last_active_datetime)

    # --- 2. HANDLE PROFILE UPDATE (POST) ---
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        bio = request.form.get('bio')
        location = request.form.get('location')

        try:
            current_user.name = full_name
            current_user.bio = bio
            current_user.location = location
            db.session.commit()
            flash('Profile updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')
        return redirect(url_for('main.profile'))

    # --- 3. STATS CALCULATION ---
    courses_count = current_user.user_enrollments.count()
    lessons_watched_count = current_user.lesson_completions.count()
    courses_completed = current_user.user_enrollments.filter_by(completed=True).count()
    active_courses = current_user.user_enrollments.filter_by(completed=False).count()

    # --- 4. TEMPLATE RENDER ---
    return render_template(
        'main/profile.html',
        user=current_user,
        courses_count=courses_count,
        courses_completed=courses_completed,
        active_courses=active_courses,
        lessons_watched_count=lessons_watched_count,
        last_active=last_active_string
    )


@main.route('/profile/avatar', methods=['POST'])
@login_required
def update_avatar():
    """Handles avatar updates using service-based avatars."""
    if 'avatar_file' in request.files and request.files['avatar_file'].filename != '':
        flash('Profile picture update acknowledged!', 'info')
    else:
        flash('Avatar settings confirmed.', 'info')

    return redirect(url_for('main.profile'))

@main.route("/healthz")
def health_check():
    return "OK", 200

@main.route('/keep-alive', methods=['POST'])
def keep_alive():
    session.permanent = True
    return ("ok", 200)