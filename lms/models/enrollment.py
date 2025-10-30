from lms import db
from datetime import datetime

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    date_enrolled = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)

    # The user relationship creates a link between Enrollment and User tables
    # - Each enrollment belongs to one user (many-to-one)
    # - user_enrollments allows accessing all enrollments for a user (one-to-many)
    # - lazy='dynamic' means the enrollments are loaded only when accessed
    user = db.relationship('User', backref=db.backref('user_enrollments', lazy='dynamic'))

    # The course relationship creates a link between Enrollment and Course tables
    # - Each enrollment belongs to one course (many-to-one)
    # - Use back_populates to link with Course.enrollments and avoid overlapping backrefs
    course = db.relationship('Course', back_populates='enrollments')

    def __repr__(self):
        return f'<Enrollment user={self.user_id} course={self.course_id}>'
