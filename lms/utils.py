# lms/utils.py
from flask_mail import Message, Mail
from flask import url_for, current_app
from lms.models.user import User 
import threading
import os
import secrets
from werkzeug.utils import secure_filename
from lms.storage import get_storage_backend


def send_async_email(app, msg):
    """Sends the email asynchronously using a thread."""
    with app.app_context():
        # Get mail from app extensions instead of importing
        mail = app.extensions.get('mail')
        if mail:
            mail.send(msg)

def send_reset_email(user: User):
    """
    Sends a password reset email to the given user.
    """
    token = user.get_reset_token()
    
    # *** IMPORTANT ***
    # _external=True generates the full URL (e.g., http://127.0.0.1:5000/auth/reset_password/...)
    reset_url = url_for('auth.reset_token', token=token, _external=True) 

    msg = Message('Password Reset Request',
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    
    msg.body = f"""
To reset your password, visit the following link:
{reset_url}

If you did not make this request, simply ignore this email and no changes will be made to your account.
The link will expire in 30 minutes.
"""
    
    # Send email in a non-blocking background thread
    threading.Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()



def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_course_image(file):
    """
    Save uploaded course image using configured storage backend.
    
    Args:
        file: FileStorage object from request.files
        
    Returns:
        str: The saved filename/identifier, or None if save failed
    """
    if file and allowed_file(file.filename):
        try:
            storage = get_storage_backend()
            return storage.save(file)
        except Exception as e:
            current_app.logger.error(f"Image save failed: {e}")
            return None
    return None

def delete_course_image(identifier):
    """
    Delete a course image using configured storage backend.
    
    Args:
        identifier: The filename or public_id to delete
    """
    if identifier:
        try:
            storage = get_storage_backend()
            storage.delete(identifier)
        except Exception as e:
            current_app.logger.error(f"Image delete failed: {e}")

def get_course_image_url(identifier):
    """
    Get URL for course image using configured storage backend.
    
    Args:
        identifier: The filename or public_id
        
    Returns:
        str: URL to the image
    """
    try:
        storage = get_storage_backend()
        return storage.url(identifier)
    except Exception as e:
        current_app.logger.error(f"Image URL generation failed: {e}")
        return '/static/img/default-course.jpg'