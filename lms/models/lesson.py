
import datetime
import re
from lms import db
from sqlalchemy import event

def slugify(s):
    """Converts a string to a URL-friendly slug."""
    s = s.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s

class Lesson(db.Model):
    __tablename__ = 'lesson'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    
    # Content fields
    content_url = db.Column(db.String(500), nullable=True)  # For YouTube/Vimeo embed
    description = db.Column(db.Text, nullable=True)
    duration = db.Column(db.String(20), nullable=True) # e.g., "10:30
    
    # Foreign Key to Module
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<Lesson {self.title}>'

# --- Event Listener to auto-generate slug ---

@event.listens_for(Lesson, 'before_insert')
def receive_before_insert(mapper, connection, target):
    """Listen for new Lesson objects and set the slug before saving."""
    if not target.slug:
        target.slug = slugify(target.title)
    
    # Ensure slug is unique
    base_slug = target.slug
    counter = 1
    while db.session.query(Lesson).filter(Lesson.slug == target.slug).first():
        target.slug = f"{base_slug}-{counter}"
        counter += 1
