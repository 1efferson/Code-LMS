# lms/models/user.py
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from lms import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    # -------------------------------
    # DB Columns
    # -------------------------------
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='student')
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    bio = db.Column(db.Text, default='')
    location = db.Column(db.String(100), default='')
    streak_last_active = db.Column(db.Date, nullable=True)
    login_streak = db.Column(db.Integer, default=0)

    # -------------------------------
    # Relationships
    # -------------------------------
    user_enrollments = db.relationship(
        'Enrollment',
        backref='user',          
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    lesson_completions = db.relationship(
        'LessonCompletion',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    # -------------------------------
    # Helper Methods
    # -------------------------------
    def get_initials(self):
        """Generates initials from the user's name."""
        if not self.name:
            return '?'
        parts = self.name.split()
        initials = parts[0][0].upper()
        if len(parts) > 1:
            initials += parts[-1][0].upper()
        return initials

    def get_reset_token(self, expires_sec=1800):
        """Generates a secure, time-limited token for password reset."""
        s = Serializer(current_app.config['SECRET_KEY'], salt='password-reset')
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        """Verifies the token and returns the user object if valid."""
        s = Serializer(current_app.config['SECRET_KEY'], salt='password-reset')
        try:
            data = s.loads(token, max_age=1800)
        except:
            return None
        return db.session.get(User, data['user_id'])

    def __repr__(self):
        return f'<User {self.email}>'
