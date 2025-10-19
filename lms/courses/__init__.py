

from flask import Blueprint

courses = Blueprint('courses', __name__,
                    template_folder='templates',
                    static_folder='static',           # lms/courses/static
                    static_url_path='/courses/static' # url_for('courses.static', filename=...)
)

from . import routes