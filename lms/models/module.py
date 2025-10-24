
import datetime
from lms import db

class Module(db.Model):
    __tablename__ = 'module'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    
    # Foreign Key to Course
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # --- Relationships ---
    
    # A Module has many Lessons
    # lazy='dynamic' allows us to use .order_by() and .count() in the template
    lessons = db.relationship(
        'Lesson', 
        backref='module', 
        lazy='dynamic', 
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Module {self.title}>'
