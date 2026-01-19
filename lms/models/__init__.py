
# lms/models/__init__.py

from lms import login_manager


# lms/models/__init__.py 
#  Import model modules so they are registered with SQLAlchemy metadata.

from .user import User
from .course import Course
from .module import Module
from .lesson import Lesson
from .lesson_completion import LessonCompletion
from .enrollment import Enrollment
from .message import Message

# Make all models available when importing from lms.models
__all__ = [
    'User',
    'Course', 
    'Module',
    'Lesson',
    'LessonCompletion',
    'Enrollment',
    'Message'
]



# user loader 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

