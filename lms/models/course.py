from lms import db
from datetime import datetime

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    published = db.Column(db.Boolean, default=False)

    # optional instructor relation (assumes User model exists)
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    instructor = db.relationship('User', backref='courses')

    def __repr__(self):
        return f'<Course {self.title}>'