# lms/models/user.py

from lms import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    # db columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='student')
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
   

    def get_initials(self):
        """
        Generates initials from the user's name.
        Example: "Alice B. Smith" -> "AS"
        """
        if not self.name:
            return '?'
        
        # Split the name into words
        parts = self.name.split()
        
        # Take the first letter of the first word
        initials = parts[0][0].upper()
        
        # If there is more than one word, take the first letter of the last word
        if len(parts) > 1:
            initials += parts[-1][0].upper()
            
        # If the name is a single word, just use the first letter
        # We ensure it's at least one letter long.
        if len(initials) == 1:
            return initials
        
        return initials

    def __repr__(self):
        return f'<User {self.email}>'