
# main __init__.py

from flask import Blueprint

main = Blueprint(
    'main',
    __name__,
    template_folder='templates'  # lms/main/templates/
)

from . import routes
