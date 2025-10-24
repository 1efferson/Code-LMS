
# main __init__.py

from flask import Blueprint

main = Blueprint(
    'main',
    __name__,
    template_folder='templates',  # lms/main/templates/
    static_folder='static',         # lms/main/static/
    static_url_path='/main/static'  # url_for('main.static', filename=...)
    
)

from . import routes
