from lms import db
from datetime import datetime

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    date_enrolled = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)

    # we use unique backref names to avoid conflicts
    user = db.relationship('User', backref=db.backref('user_enrollments', lazy='dynamic'))
    course = db.relationship('Course', backref=db.backref('course_enrollments', lazy='dynamic'))

    def __repr__(self):
        return f'<Enrollment user={self.user_id} course={self.course_id}>'
