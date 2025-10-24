import datetime
import re
from lms import db
from sqlalchemy import event

def slugify(s):
    """Converts a string to a URL-friendly slug."""
    if not s:
        return ""
    s = s.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s


class Course(db.Model):
    __tablename__ = 'course'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    published = db.Column(db.Boolean, default=False, nullable=False)
    
    level = db.Column(db.String(50), default='Beginner', nullable=True)
    category = db.Column(db.String(100), nullable=True)

    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    instructor = db.relationship('User', backref='courses_taught', foreign_keys=[instructor_id])
    
    # Updated relationship (uses back_populates)
    enrollments = db.relationship('Enrollment', back_populates='course', lazy='dynamic', cascade='all, delete-orphan')

    modules = db.relationship('Module', backref='course', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Course {self.title}>'


@event.listens_for(Course, 'before_insert')
def receive_before_insert(mapper, connection, target):
    """Listen for new Course objects and set the slug before saving."""
    if not target.slug:
        target.slug = slugify(target.title)
    
    # Ensure slug is unique
    base_slug = target.slug
    counter = 1
    while db.session.query(Course).filter(Course.slug == target.slug).first():
        target.slug = f"{base_slug}-{counter}"
        counter += 1
