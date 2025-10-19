
# lms/auth/__init__.py
from flask import Blueprint

auth = Blueprint(
    'auth',
    __name__,
    template_folder='templates'
)

from . import routes
