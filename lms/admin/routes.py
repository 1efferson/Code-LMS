# lms/admin/routes.py (Complete Code with FIXES and NEW ROUTES)
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from lms import db
# Import necessary models
from lms.models.course import Course
from lms.models.module import Module 
from lms.models.lesson import Lesson 
from . import admin
# Import the newly defined forms
from .forms import CourseForm, ModuleForm, LessonForm
from slugify import slugify 

def is_admin(user):
    """Helper to check if the current user is an admin."""
    return getattr(user, 'is_admin', False)

# --- Admin Index and Existing Course Routes (FIXED) ---

@admin.route('/')
@login_required
def admin_index():
    if not is_admin(current_user):
        flash("You don't have permission to access the admin area.", "danger")
        return redirect(url_for('courses.index'))
    return redirect(url_for('admin.manage_courses'))


@admin.route('/courses/add', methods=['GET', 'POST'])
@login_required
def add_course():
    """Admin-only route for adding new courses (FIXED to handle instructor)."""
    if not is_admin(current_user):
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('courses.index'))

    form = CourseForm()

    if form.validate_on_submit():
        # Get the instructor object from the QuerySelectField
        instructor_user = form.instructor.data
        instructor_id = instructor_user.id if instructor_user else None
        
        course = Course(
            title=form.title.data,
            slug=slugify(form.title.data),
            description=form.description.data,
            level=form.level.data,
            category=form.category.data,
            published=form.published.data,
            # FIX: Assign the instructor ID
            instructor_id=instructor_id 
        )
        db.session.add(course)
        db.session.commit()
        flash(f'Course "{course.title}" created successfully! Now build the course outline.', 'success')
        
        # Redirect to the NEW course outline page instead of manage_courses
        return redirect(url_for('admin.manage_course_outline', course_id=course.id)) 

    return render_template('admin/add_course.html', form=form)


@admin.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    """Admin-only route for editing existing courses (FIXED to handle instructor)."""
    if not is_admin(current_user):
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('courses.index'))

    course = db.session.get(Course, course_id)
    if course is None:
        flash("Course not found.", "danger")
        return redirect(url_for('admin.manage_courses'))

    form = CourseForm(obj=course)

    if form.validate_on_submit():
        # Get the instructor object from the QuerySelectField
        instructor_user = form.instructor.data
        course.instructor_id = instructor_user.id if instructor_user else None
        
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
    if not is_admin(current_user):
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('courses.index'))
    
    all_courses = Course.query.order_by(Course.created_at.desc()).all()
    
    return render_template('admin/manage_courses.html', courses=all_courses)

# --- Toggle Publish & Delete Actions (No change needed) ---

@admin.route('/courses/<int:course_id>/toggle_publish', methods=['POST'])
@login_required
def toggle_publish(course_id):
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

# --- NEW Course Outline and Content Management Routes ---

@admin.route('/courses/<int:course_id>/outline')
@login_required
def manage_course_outline(course_id):
    """NEW: Admin-only route to view and manage modules and lessons for a specific course."""
    if not is_admin(current_user):
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('courses.index'))
        
    course = db.session.get(Course, course_id)
    if course is None:
        flash("Course not found.", "danger")
        return redirect(url_for('admin.manage_courses'))

    # Pass new Module and Lesson form instances to the template
    return render_template(
        'admin/admin_course_outline.html', 
        course=course, 
        module_form=ModuleForm(),
        lesson_form=LessonForm()
    )


@admin.route('/modules/add/<int:course_id>', methods=['POST'])
@login_required
def add_module(course_id):
    """NEW: Route to handle adding a new module to a course."""
    if not is_admin(current_user):
        flash("You don't have permission to perform this action.", "danger")
        return redirect(url_for('courses.index'))

    course = db.session.get(Course, course_id)
    module_form = ModuleForm()

    if course and module_form.validate_on_submit():
        new_module = Module(
            title=module_form.title.data,
            order=module_form.order.data,
            course_id=course.id # Foreign key is set
        )
        db.session.add(new_module)
        db.session.commit()
        flash(f'Module "{new_module.title}" added successfully.', 'success')
    else:
        flash('Module creation failed. Check input data.', 'danger')
        
    return redirect(url_for('admin.manage_course_outline', course_id=course_id))

# --- Module Edit/Delete Routes ---

@admin.route('/modules/<int:module_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_module(module_id):
    """FIX: Admin-only route for editing a specific module, redirects to outline."""
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
        # FIX: Redirect back to the course outline page
        return redirect(url_for('admin.manage_course_outline', course_id=course_id))
    
    form.submit.label.text = 'Save Module Changes'
    return render_template('admin/edit_module.html', form=form, module=module, course_id=course_id)


@admin.route('/modules/<int:module_id>/delete', methods=['POST'])
@login_required
def delete_module(module_id):
    """FIX: Route to handle deleting a module and its associated lessons."""
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
        # Deleting the module will automatically delete associated lessons (assuming cascading delete is set up in the model)
        db.session.delete(module)
        db.session.commit()
        flash(f'Module "{module_title}" and all its lessons have been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the module: {e}', 'danger')
        
    # FIX: Always redirect back to the course outline
    return redirect(url_for('admin.manage_course_outline', course_id=course_id))


# --- Lesson Add/Edit/Delete Routes ---

@admin.route('/lessons/add/<int:module_id>', methods=['POST'])
@login_required
def add_lesson(module_id):
    """NEW: Route to handle adding a new lesson to a module."""
    if not is_admin(current_user):
        flash("You don't have permission to perform this action.", "danger")
        return redirect(url_for('courses.index'))

    module = db.session.get(Module, module_id)
    lesson_form = LessonForm()

    course_id = None
    if module:
        course_id = module.course_id

    if module and lesson_form.validate_on_submit():
        new_lesson = Lesson(
            title=lesson_form.title.data,
            content_url=lesson_form.content_url.data,
            description=lesson_form.description.data,
            duration=lesson_form.duration.data,
            order=lesson_form.order.data,
            module_id=module.id # Foreign key is set
        )
        db.session.add(new_lesson)
        db.session.commit()
        flash(f'Lesson "{new_lesson.title}" added successfully.', 'success')
        
        return redirect(url_for('admin.manage_course_outline', course_id=course_id))

    else:
        if course_id is None:
            # Fallback for redirection if the module object was not found initially
            course_id = request.form.get('course_id') # Attempt to retrieve from form (if available)
        
        flash('Lesson creation failed. Check input data.', 'danger')
        # If we have a course_id, redirect back to the outline, otherwise manage_courses
        if course_id:
            return redirect(url_for('admin.manage_course_outline', course_id=course_id))
        else:
             return redirect(url_for('admin.manage_courses'))


@admin.route('/lessons/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_lesson(lesson_id):
    """FIX: Admin-only route for editing a specific lesson, redirects to outline."""
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
        # Update lesson fields
        lesson.title = form.title.data
        lesson.content_url = form.content_url.data
        lesson.description = form.description.data
        lesson.duration = form.duration.data
        lesson.order = form.order.data
        
        db.session.commit()
        flash(f'Lesson "{lesson.title}" updated successfully!', 'success')
        # FIX: Redirect back to the course outline page
        return redirect(url_for('admin.manage_course_outline', course_id=course_id))
    
    # If GET request or validation failed
    form.submit.label.text = 'Save Lesson Changes'
    return render_template('admin/edit_lesson.html', form=form, lesson=lesson, course_id=course_id)


@admin.route('/lessons/<int:lesson_id>/delete', methods=['POST'])
@login_required
def delete_lesson(lesson_id):
    """FIX: Route to handle deleting a specific lesson."""
    if not is_admin(current_user):
        flash("You don't have permission to perform this action.", "danger")
        return redirect(url_for('courses.index'))

    lesson = db.session.get(Lesson, lesson_id)

    if lesson is None:
        flash("Lesson not found.", "danger")
        # If lesson not found, redirect to manage courses as we can't reliably get course_id
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
        
    # FIX: Redirect back to the course outline
    return redirect(url_for('admin.manage_course_outline', course_id=course_id))
