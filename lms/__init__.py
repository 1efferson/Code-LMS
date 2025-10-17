
# lms/__init__.py

from flask import Flask
from .extensions import db,  login_manager, csrf, bcrypt

# Import blueprints from route files
from .main import main as main_blueprint
from .auth import auth as auth_blueprint

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
    
    # Flask-Login configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    
    # Register Blueprints
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    # User loader
    from .models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    return app
