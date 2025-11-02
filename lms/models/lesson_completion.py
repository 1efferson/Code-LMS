# lms/models/lesson_completion.py
import datetime
from lms import db

class LessonCompletion(db.Model):
    __tablename__ = 'lesson_completion'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    
    # Timestamps
    completed_at = db.Column( db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), # Use timezone-aware 'now'
    nullable=False
)

    # Constraint to prevent duplicates (a user can only complete a lesson once)
    __table_args__ = (db.UniqueConstraint('user_id', 'lesson_id', name='_user_lesson_uc'),)


    lesson = db.relationship('Lesson', backref='completions') 

    def __repr__(self):
        return f'<LessonCompletion User:{self.user_id} Lesson:{self.lesson_id}>'