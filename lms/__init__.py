
# lms/__init__.py

from flask import Flask
from .extensions import db, login_manager, csrf, bcrypt, migrate
import logging

# Import blueprints from route files
from .main import main as main_blueprint
from .auth import auth as auth_blueprint
from .courses.routes import courses as courses_blueprint

# Module-level user loader (lazy-import User to avoid circular imports)
@login_manager.user_loader
def load_user(user_id):
    logger = logging.getLogger(__name__)
    logger.debug("module-level load_user called with user_id=%r", user_id)
    if not user_id:
        return None
    try:
        # importing inside function to avoid circular import at module import time
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

    # Importing models so Alembic sees metadata (side-effect import)
    from . import models 

    # ---- CLI: seed demo data ----
    @app.cli.command('seed-demo')
    def seed_demo():
        """Populate the database with demo courses, a demo student, and enrollments."""
        from .models.user import User
        from .models.course import Course
        from .models.enrollment import Enrollment
        from .extensions import db, bcrypt

        # Create a demo instructor
        instructor = User.query.filter_by(email='instructor@example.com').first()
        if not instructor:
            instructor = User(name='Instructor One', email='instructor@example.com',
                              password=bcrypt.generate_password_hash('password123').decode('utf-8'),
                              role='instructor')
            db.session.add(instructor)

        # Create a demo student
        student = User.query.filter_by(email='student@example.com').first()
        if not student:
            student = User(name='Demo Student', email='student@example.com',
                           password=bcrypt.generate_password_hash('password123').decode('utf-8'),
                           role='student')
            db.session.add(student)
        
        # Demo courses (published)
        demo_courses = [
            {
                'title': 'Python Fundamentals',
                'description': 'Learn the basics of Python programming, including syntax, data types, and control flow.',
                'level': 'Beginner',
                'category': 'Programming'
            },
            {
                'title': 'Introduction to JavaScript',
                'description': 'Learn the basics of JavaScript programming, including syntax, data types, and control flow.',
                'level': 'Beginner',
                'category': 'Programming'
            },
            {
                'title': 'Web Development with Flask',
                'description': 'Build dynamic web applications using Flask, Jinja2, and SQLAlchemy.',
                'level': 'Intermediate',
                'category': 'Web Development'
            },
            {
                'title': 'Data Analysis with Pandas',
                'description': 'Use Pandas to clean, analyze, and visualize data effectively.',
                'level': 'Intermediate',
                'category': 'Data Science'
            },
            {
                'title': 'Algorithms and Data Structures',
                'description': 'Master the fundamental data structures and algorithms used in technical interviews.',
                'level': 'Advanced',
                'category': 'Computer Science'
            }
        ]

        created_courses = []
        for c in demo_courses:
            existing = Course.query.filter_by(title=c['title']).first()
            if existing:
                course = existing
            else:
                course = Course(
                    title=c['title'],
                    description=c['description'],
                    level=c.get('level'),
                    category=c.get('category'),
                    instructor_id=instructor.id if instructor else None,
                    published=True
                )
                db.session.add(course)
            created_courses.append(course)

        db.session.commit()  # ensure IDs for users and courses

        # Ensure the demo student is enrolled in exactly ONE Beginner course
        # 1) Find a Beginner-level course (create one above if not exists)
        beginner_course = next((c for c in created_courses if (c.level or '').lower() == 'beginner'), None)

        if beginner_course:
            # 2) Remove any existing enrollments for the student that are NOT the Beginner course
            existing_others = Enrollment.query.filter(
                Enrollment.user_id == student.id,
                Enrollment.course_id != beginner_course.id
            ).all()
            for e in existing_others:
                db.session.delete(e)

            # 3) Ensure enrollment exists for the Beginner course only
            existing_beginner = Enrollment.query.filter_by(user_id=student.id, course_id=beginner_course.id).first()
            if not existing_beginner:
                db.session.add(Enrollment(user_id=student.id, course_id=beginner_course.id))

        db.session.commit()
        print('Seed complete. Login as student@example.com / password123 to view enrollments on dashboard.')
    
    # ---- CLI: clear all data (keep tables) ----
    @app.cli.command('clear-data')
    def clear_data():
        """Delete all rows from all tables while preserving the schema."""
        from .extensions import db
        from sqlalchemy import text

        engine = db.engine
        with engine.connect() as connection:
            trans = connection.begin()
            try:
                # Temporarily disable FK constraints for SQLite to avoid delete order issues
                if engine.dialect.name == 'sqlite':
                    connection.execute(text('PRAGMA foreign_keys = OFF'))

                # Delete from all tables in reverse dependency order
                for table in reversed(db.metadata.sorted_tables):
                    connection.execute(table.delete())

                trans.commit()
            except Exception:
                trans.rollback()
                raise
            finally:
                if engine.dialect.name == 'sqlite':
                    connection.execute(text('PRAGMA foreign_keys = ON'))
        print('All data cleared. Tables remain intact.')
    
    return app
