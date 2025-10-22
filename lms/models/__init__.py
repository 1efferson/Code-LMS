
# lms/models/__init__.py

from lms import login_manager

#  Import model modules so they are registered with SQLAlchemy metadata.
from .user import User
from .course import Course

# export names for convenience
__all__ = ["User", "Course"]


# user loader 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))