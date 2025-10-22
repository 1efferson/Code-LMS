
# lms/__init__.py

from flask import Flask
from .extensions import db, login_manager, csrf, bcrypt, migrate
import logging

# Import blueprints from route files
from .main import main as main_blueprint
from .auth import auth as auth_blueprint
from .courses import courses as courses_blueprint

# Module-level user loader (lazy-import User to avoid circular imports)
@login_manager.user_loader
def load_user(user_id):
    logger = logging.getLogger(__name__)
    logger.debug("module-level load_user called with user_id=%r", user_id)
    if not user_id:
        return None
    try:
        # import inside function to avoid circular import at module import time
        from .models.user import User
        return db.session.get(User, int(user_id))
    except Exception:
        logger.exception("Error in module-level load_user")
        return None


def create_app(config_object='config.Config'):
    """Application factory for the LMS."""

    
    # Initialize Flask app
    app = Flask('lms', instance_relative_config=True)
    
    # Load configuration
    app.config.from_object(config_object)
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    
    # Flask-Login configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    
    # Register Blueprints
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(courses_blueprint, url_prefix='/courses')

    # Import models so Alembic sees metadata (side-effect import)
    from . import models  # lms/models/__init__.py should import all models
    
    return app
