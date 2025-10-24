
# lms/courses/__init__.py

from flask import Blueprint

courses = Blueprint(
    'courses',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/courses/static', 
    url_prefix='/courses'
)
# This attaches all the routes from 'routes.py' to the blueprint above
from . import routes
