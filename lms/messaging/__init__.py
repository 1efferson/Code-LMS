# lms/messaging/__init__.py

from flask import Blueprint

# Create the messaging blueprint
messaging = Blueprint(
    'messaging',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# Import routes after blueprint creation to avoid circular imports
from . import routes