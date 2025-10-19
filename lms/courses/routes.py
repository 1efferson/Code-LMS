from flask import render_template
from . import courses
from lms.models.course import Course

@courses.route('/', methods=['GET'])
def index():
    items = Course.query.filter_by(published=True).order_by(Course.created_at.desc()).all()
    return render_template('courses/course_catalog.html', courses=items)

@courses.route('/<slug>', methods=['GET'])
def detail(slug):
    course = Course.query.filter_by(slug=slug).first_or_404()
    return render_template('courses/detail.html', course=course)