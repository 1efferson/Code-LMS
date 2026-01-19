# lms/messaging/models.py

from lms.extensions import db
from datetime import datetime


class Message(db.Model):
    """
    Message model for instructor-to-student messaging.
    
    Security features:
    - Foreign key constraints ensure data integrity
    - Timestamps for audit trail
    - Read status tracking
    - Soft delete capability (optional)
    """
    
    __tablename__ = 'messages'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    sender_id = db.Column(
        db.Integer, 
        db.ForeignKey('user.id', ondelete='CASCADE'), 
        nullable=False,
        index=True  # Index for faster queries
    )
    receiver_id = db.Column(
        db.Integer, 
        db.ForeignKey('user.id', ondelete='CASCADE'), 
        nullable=False,
        index=True  # Index for faster queries
    )
    
    # Message Content
    content = db.Column(db.Text, nullable=False)
    subject = db.Column(db.String(200), nullable=True)  # Optional subject line
    
    # Status Tracking
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Soft Delete (optional - for audit trail)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    sender = db.relationship(
        'User',
        foreign_keys=[sender_id],
        backref=db.backref('sent_messages', lazy='dynamic', cascade='all, delete-orphan')
    )
    
    receiver = db.relationship(
        'User',
        foreign_keys=[receiver_id],
        backref=db.backref('received_messages', lazy='dynamic', cascade='all, delete-orphan')
    )
    
    # Composite index for common queries (sender + receiver + timestamp)
    __table_args__ = (
        db.Index('idx_sender_receiver', 'sender_id', 'receiver_id'),
        db.Index('idx_receiver_read', 'receiver_id', 'is_read'),
    )
    
    def mark_as_read(self):
        """Mark message as read and set read timestamp."""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
            db.session.commit()
    
    def soft_delete(self):
        """Soft delete the message (keeps in database for audit)."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        db.session.commit()
    
    def time_ago(self):
        """Return human-readable time ago string."""
        from lms.main.routes import time_ago_in_words
        return time_ago_in_words(self.created_at)
    
    def __repr__(self):
        return f'<Message from={self.sender_id} to={self.receiver_id} at={self.created_at}>'