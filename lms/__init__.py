# lms/__init__.py

from flask import Flask
from .extensions import db, login_manager, csrf, bcrypt, migrate
from flask_mail import Mail
import logging

# Import blueprints
from .main import main as main_blueprint
from .auth import auth as auth_blueprint
from .courses.routes import courses as courses_blueprint
from .admin import admin as admin_blueprint
from lms.commands import promote_admin
from lms.instructor import instructor



mail = Mail()  # ✅ initialize Flask-Mail globally


@login_manager.user_loader
def load_user(user_id):
    logger = logging.getLogger(__name__)
    logger.debug("module-level load_user called with user_id=%r", user_id)
    if not user_id:
        return None
    try:
        from .models.user import User  # avoid circular import
        return db.session.get(User, int(user_id))
    except Exception:
        logger.exception("Error in module-level load_user")
        return None


def create_app(config_object='config.Config'):
    """Application factory for the LMS."""

    app = Flask('lms', instance_relative_config=True)
    app.config.from_object(config_object)

    # CLI command
    app.cli.add_command(promote_admin)
    
    # Initialize extensions 
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)  
    
    # Flask-Login config
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    
    # Register Blueprints
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(courses_blueprint, url_prefix='/courses')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(instructor, url_prefix='/instructor')

    # Import models for Alembic
    from . import models 
    
    return app
