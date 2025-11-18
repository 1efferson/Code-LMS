import datetime
from lms import db

class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    course = db.relationship('Course', backref='messages')

    def __repr__(self):
        return f'<Message from {self.sender.name} to {self.receiver.name} in {self.course.title}>'
