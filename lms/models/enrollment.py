from lms import db
from datetime import datetime

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    date_enrolled = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    date_completed = db.Column(db.DateTime, nullable=True)

    # Relationships
    course = db.relationship('Course', backref=db.backref('enrollments', lazy='dynamic'))

    def __repr__(self):
        return f'<Enrollment user={self.user_id} course={self.course_id}>'

    # --------------------------------------------------------
    # Helper Method: Mark course completed if all lessons done
    # --------------------------------------------------------
    def check_and_update_completion(self):
        """Marks this enrollment as completed if all lessons in the course are finished by the user."""
        from lms.models.lesson_completion import LessonCompletion
        from lms.models.lesson import Lesson

        # Count total lessons for the course
        total_lessons = 0
        for module in self.course.modules:
            total_lessons += module.lessons.count()  # Use .count() for dynamic relationships

        if total_lessons == 0:
            return False  # No lessons to complete

        # Count completed lessons by this user
        completed_lessons = (
            LessonCompletion.query
            .join(Lesson)
            .filter(
                LessonCompletion.user_id == self.user_id,
                Lesson.module_id.in_([m.id for m in self.course.modules])
            )
            .count()
        )

        # Update enrollment if all lessons completed
        if completed_lessons == total_lessons and not self.completed:
            self.completed = True
            self.date_completed = datetime.utcnow()
            db.session.commit()
            return True
        elif completed_lessons < total_lessons and self.completed:
            # Reset completion if a lesson was unmarked
            self.completed = False
            self.date_completed = None
            db.session.commit()
            return True

        return False
