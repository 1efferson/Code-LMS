from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from lms.models import User 

# Form for registering new users
class RegisterForm(FlaskForm):
    # User's full name (required, between 2 and 100 characters)
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    
    # User's email (required, must be a valid email format)
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    # Password field (required, minimum of 6 characters)
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    
    # Confirm password field (must match the password above)
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    
    # Optional field for admin registration (not required)
    admin_code = StringField('Admin Code (optional)')
    
    # Button to submit the registration form
    submit = SubmitField('Register')

    # Custom validation to ensure each email is unique
    def validate_email(self, email):
        # Check if the entered email already exists in the database
        existing_user = User.query.filter_by(email=email.data).first()
        if existing_user:
            # Raise an error if the email is already registered
            raise ValidationError('A user with this email already exists. Please log in instead.')


# Form for user login
class LoginForm(FlaskForm):
    # Email field (required, must be valid)
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    # Password field (required)
    password = PasswordField('Password', validators=[DataRequired()])
    
    # Submit button for logging in
    submit = SubmitField('Login')


# Form for users who forgot their password
class ForgotPasswordForm(FlaskForm):
    # Only needs the email to send the reset link
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    # Button to send password reset email
    submit = SubmitField('Send Reset Link')


# Form for resetting password using a token link
class ResetPasswordForm(FlaskForm):
    # New password field (required, minimum 6 characters)
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    
    # Must match the new password field
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    
    # Button to submit new password
    submit = SubmitField('Reset Password')
