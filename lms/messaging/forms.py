# lms/messaging/forms.py

from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, HiddenField
from wtforms.validators import DataRequired, Length, Optional


class SendMessageForm(FlaskForm):
    """
    Form for sending messages from instructor to student.
    
    Security features:
    - CSRF protection via FlaskForm
    - Input length validation
    - XSS prevention through template escaping
    """
    
    receiver_id = HiddenField(
        'Receiver ID',
        validators=[DataRequired()]
    )
    
    subject = StringField(
        'Subject',
        validators=[
            Optional(),
            Length(max=200, message='Subject must be less than 200 characters')
        ],
        render_kw={
            'placeholder': 'Subject (optional)',
            'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100'
        }
    )
    
    content = TextAreaField(
        'Message',
        validators=[
            DataRequired(message='Message content is required'),
            Length(min=1, max=5000, message='Message must be between 1 and 5000 characters')
        ],
        render_kw={
            'placeholder': 'Type your message here...',
            'rows': 5,
            'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100'
        }
    )


class MarkAsReadForm(FlaskForm):
    """
    Form for marking messages as read.
    Simple form that only needs CSRF protection.
    """
    message_id = HiddenField(
        'Message ID',
        validators=[DataRequired()]
    )