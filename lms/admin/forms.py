


    
# lms/admin/forms.py (Complete Code)
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Optional
# QuerySelectField is ideal for selecting a related database object (the Instructor)
from wtforms_sqlalchemy.fields import QuerySelectField
from lms.models.user import User # Assuming your User model is imported correctly

# --- Query Functions for QuerySelectField ---

def get_instructors_query():
    """Returns a query of users who can be instructors (role is 'admin' or 'instructor')."""
    
    # FIX: Filter users where role is explicitly 'instructor' or 'admin'
    return User.query.filter(
        User.role.in_(['admin', 'instructor']) 
    ).order_by(User.name).all()

def display_instructor_label(user):
    """Formats the label displayed in the dropdown using the user's name."""
    
    # FIX: Use user.name and user.email for clear display
    return f"{user.name} ({user.email})"

# --- Course Management Forms ---

COURSE_LEVEL_CHOICES = [
    ('Beginner', 'Beginner'),
    ('Intermediate', 'Intermediate'),
    ('Advanced', 'Advanced')
]

class CourseForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    
    # NEW FIELD: Instructor Selection
    # This solves the Jinja2 UndefinedError
    instructor = QuerySelectField(
        'Instructor',
        query_factory=get_instructors_query,
        get_label=display_instructor_label,
        allow_blank=True,
        blank_text='-- Select Course Instructor --',
        # Set to Optional since a course might not have an instructor assigned yet
        validators=[Optional()] 
    )
    
    level = SelectField('Course Level', 
                        choices=COURSE_LEVEL_CHOICES, 
                        validators=[DataRequired()],
                        default='Beginner')
                        
    category = StringField('Category (e.g., Python, Version Control)', validators=[DataRequired(), Length(max=100)])
    
    published = BooleanField('Publish Now?')
    submit = SubmitField('Save Course') 


class ModuleForm(FlaskForm):
    """Form for adding/editing a Module."""
    title = StringField('Module Title', validators=[DataRequired(), Length(max=200)])
    # Integer field for setting the display order/sequence
    order = IntegerField('Order/Sequence', default=1, validators=[DataRequired()])
    submit = SubmitField('Save Module')


class LessonForm(FlaskForm):
    """Form for adding/editing a Lesson."""
    title = StringField('Lesson Title', validators=[DataRequired(), Length(max=200)])
    
    # Field corresponding to the Lesson.content_url
    content_url = StringField('Video Content URL (Embed)', validators=[Optional(), Length(max=500)])
    
    # Field corresponding to the Lesson.description
    description = TextAreaField('Lesson Notes/Description', validators=[Optional()])
    
    # Field corresponding to the Lesson.duration
    duration = StringField('Duration (e.g., 10:30)', validators=[Optional(), Length(max=20)])
    
    # Field corresponding to the Lesson.order
    order = IntegerField('Order/Sequence', default=1, validators=[DataRequired()])
    
    submit = SubmitField('Save Lesson')