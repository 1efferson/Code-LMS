# lms/admin/routes.py (Complete Code with Comments)
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from lms import db
from lms.models.course import Course
from lms.models.module import Module 
from lms.models.lesson import Lesson 
from . import admin
from .forms import CourseForm, ModuleForm, LessonForm
from slugify import slugify 

def is_admin(user):
    """Helper to check if the current user is an admin."""
    return getattr(user, 'is_admin', False)

# ===============================
# ADMIN INDEX AND COURSE ROUTES
# ===============================

@admin.route('/')
@login_required
def admin_index():
    """Redirects admins to the course management page."""
    if not is_admin(current_user):
        flash("You don't have permission to access the admin area.", "danger")
        return redirect(url_for('courses.index'))
    return redirect(url_for('admin.manage_courses'))


@admin.route('/courses/add', methods=['GET', 'POST'])
@login_required
def add_course():
    """Allows admins to create a new course with instructor assignment."""
    if not is_admin(current_user):
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('courses.index'))

    form = CourseForm()

    if form.validate_on_submit():
        # Retrieve instructor from the form
        instructor_user = form.instructor.data
        instructor_id = instructor_user.id if instructor_user else None
        
        # Create a new course instance
        course = Course(
            title=form.title.data,
            slug=slugify(form.title.data),
            description=form.description.data,
            level=form.level.data,
            category=form.category.data,
            published=form.published.data,
            instructor_id=instructor_id
        )
        db.session.add(course)
        db.session.commit()

        flash(f'Course "{course.title}" created successfully! Now build the course outline.', 'success')
        # Redirect directly to the outline builder
        return redirect(url_for('admin.manage_course_outline', course_id=course.id)) 

    return render_template('admin/add_course.html', form=form)


@admin.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    """Enables admins to edit an existing course."""
    if not is_admin(current_user):
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('courses.index'))

    course = db.session.get(Course, course_id)
    if course is None:
        flash("Course not found.", "danger")
        return redirect(url_for('admin.manage_courses'))

    form = CourseForm(obj=course)

    if form.validate_on_submit():
        # Update instructor information
        instructor_user = form.instructor.data
        course.instructor_id = instructor_user.id if instructor_user else None
        
        # Update course attributes
        course.title = form.title.data
        if db.session.is_modified(course, 'title'):
            course.slug = slugify(form.title.data)
            
        course.description = form.description.data
        course.level = form.level.data
        course.category = form.category.data
        course.published = form.published.data
        
        db.session.commit()
        flash(f"Course '{course.title}' updated successfully!", 'success')
        return redirect(url_for('admin.manage_courses'))

    form.submit.label.text = 'Save Changes'
    return render_template('admin/edit_course.html', form=form, course=course)


@admin.route('/courses/manage')
@login_required
def manage_courses():
    """Displays all courses to the admin."""
    if not is_admin(current_user):
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('courses.index'))
    
    all_courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template('admin/manage_courses.html', courses=all_courses)

# ===============================
# COURSE ACTIONS (PUBLISH/DELETE)
# ===============================

@admin.route('/courses/<int:course_id>/toggle_publish', methods=['POST'])
@login_required
def toggle_publish(course_id):
    """Allows admins to toggle a course’s publish status."""
    if not is_admin(current_user):
        flash("You don't have permission to perform this action.", "danger")
        return redirect(url_for('courses.index'))

    course = db.session.get(Course, course_id)
    
    if course is None:
        flash("Course not found.", "danger")
    else:
        course.published = not course.published
        db.session.commit()
        status = "published" if course.published else "Moved to Drafts"
        flash(f"Course '{course.title}' has been {status}.", "success")
    
    return redirect(url_for('admin.manage_courses'))


@admin.route('/courses/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    """Deletes a course and all associated content."""
    if not is_admin(current_user):
        flash("You don't have permission to perform this action.", "danger")
        return redirect(url_for('courses.index'))

    course = db.session.get(Course, course_id)
    
    if course is None:
        flash("Course not found.", "danger")
    else:
        course_title = course.title
        db.session.delete(course)
        db.session.commit()
        flash(f"Course '{course_title}' and all related content have been permanently deleted.", "success")
    
    return redirect(url_for('admin.manage_courses'))

# ===============================
# COURSE OUTLINE AND MODULE ROUTES
# ===============================

@admin.route('/courses/<int:course_id>/outline')
@login_required
def manage_course_outline(course_id):
    """Displays the full structure of a course (modules and lessons)."""
    if not is_admin(current_user):
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('courses.index'))
        
    course = db.session.get(Course, course_id)
    if course is None:
        flash("Course not found.", "danger")
        return redirect(url_for('admin.manage_courses'))

    # Send forms for adding new modules and lessons
    return render_template(
        'admin/admin_course_outline.html', 
        course=course, 
        module_form=ModuleForm(),
        lesson_form=LessonForm()
    )


@admin.route('/modules/add/<int:course_id>', methods=['POST'])
@login_required
def add_module(course_id):
    """Creates a new module for a specific course."""
    if not is_admin(current_user):
        flash("You don't have permission to perform this action.", "danger")
        return redirect(url_for('courses.index'))

    course = db.session.get(Course, course_id)
    module_form = ModuleForm()

    if course and module_form.validate_on_submit():
        new_module = Module(
            title=module_form.title.data,
            order=module_form.order.data,
            course_id=course.id
        )
        db.session.add(new_module)
        db.session.commit()
        flash(f'Module "{new_module.title}" added successfully.', 'success')
    else:
        flash('Module creation failed. Check input data.', 'danger')
        
    return redirect(url_for('admin.manage_course_outline', course_id=course_id))


@admin.route('/modules/<int:module_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_module(module_id):
    """Allows admins to edit a module."""
    if not is_admin(current_user):
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('courses.index'))
        
    module = db.session.get(Module, module_id)
    if module is None:
        flash("Module not found.", "danger")
        return redirect(url_for('admin.manage_courses'))

    course_id = module.course_id
    form = ModuleForm(obj=module)
    
    if form.validate_on_submit():
        module.title = form.title.data
        module.order = form.order.data
        db.session.commit()
        flash(f'Module "{module.title}" updated successfully!', 'success')
        return redirect(url_for('admin.manage_course_outline', course_id=course_id))
    
    form.submit.label.text = 'Save Module Changes'
    return render_template('admin/edit_module.html', form=form, module=module, course_id=course_id)


@admin.route('/modules/<int:module_id>/delete', methods=['POST'])
@login_required
def delete_module(module_id):
    """Deletes a module and all associated lessons."""
    if not is_admin(current_user):
        flash("You don't have permission to perform this action.", "danger")
        return redirect(url_for('courses.index'))

    module = db.session.get(Module, module_id)
    
    if module is None:
        flash("Module not found.", "danger")
        return redirect(url_for('admin.manage_courses'))

    course_id = module.course_id
    module_title = module.title

    try:
        db.session.delete(module)
        db.session.commit()
        flash(f'Module "{module_title}" and all its lessons have been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the module: {e}', 'danger')
        
    return redirect(url_for('admin.manage_course_outline', course_id=course_id))

# ===============================
# LESSON ROUTES
# ===============================

@admin.route('/lessons/add/<int:module_id>', methods=['POST'])
@login_required
def add_lesson(module_id):
    """Adds a new lesson to a specific module."""
    if not is_admin(current_user):
        flash("You don't have permission to perform this action.", "danger")
        return redirect(url_for('courses.index'))

    module = db.session.get(Module, module_id)
    lesson_form = LessonForm()
    course_id = module.course_id if module else None

    if module and lesson_form.validate_on_submit():
        new_lesson = Lesson(
            title=lesson_form.title.data,
            content_url=lesson_form.content_url.data,
            description=lesson_form.description.data,
            duration=lesson_form.duration.data,
            order=lesson_form.order.data,
            module_id=module.id
        )
        db.session.add(new_lesson)
        db.session.commit()
        flash(f'Lesson "{new_lesson.title}" added successfully.', 'success')
        return redirect(url_for('admin.manage_course_outline', course_id=course_id))
    else:
        if course_id is None:
            course_id = request.form.get('course_id')
        flash('Lesson creation failed. Check input data.', 'danger')
        return redirect(url_for('admin.manage_course_outline', course_id=course_id)) if course_id else redirect(url_for('admin.manage_courses'))


@admin.route('/lessons/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_lesson(lesson_id):
    """Allows admins to edit a specific lesson."""
    if not is_admin(current_user):
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('courses.index'))
        
    lesson = db.session.get(Lesson, lesson_id)
    if lesson is None:
        flash("Lesson not found.", "danger")
        return redirect(url_for('admin.manage_courses'))

    course_id = lesson.module.course_id
    form = LessonForm(obj=lesson)
    
    if form.validate_on_submit():
        lesson.title = form.title.data
        lesson.content_url = form.content_url.data
        lesson.description = form.description.data
        lesson.duration = form.duration.data
        lesson.order = form.order.data
        
        db.session.commit()
        flash(f'Lesson "{lesson.title}" updated successfully!', 'success')
        return redirect(url_for('admin.manage_course_outline', course_id=course_id))
    
    form.submit.label.text = 'Save Lesson Changes'
    return render_template('admin/edit_lesson.html', form=form, lesson=lesson, course_id=course_id)


@admin.route('/lessons/<int:lesson_id>/delete', methods=['POST'])
@login_required
def delete_lesson(lesson_id):
    """Deletes a specific lesson."""
    if not is_admin(current_user):
        flash("You don't have permission to perform this action.", "danger")
        return redirect(url_for('courses.index'))

    lesson = db.session.get(Lesson, lesson_id)

    if lesson is None:
        flash("Lesson not found.", "danger")
        return redirect(url_for('admin.manage_courses'))
    
    course_id = lesson.module.course_id
    lesson_title = lesson.title
    
    try:
        db.session.delete(lesson)
        db.session.commit()
        flash(f'Lesson "{lesson_title}" deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the lesson: {e}', 'danger')
        
    return redirect(url_for('admin.manage_course_outline', course_id=course_id))
