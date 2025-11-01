from flask_mail import Message
from flask import url_for, current_app
from lms.__init__ import mail # Assuming you import mail from __init__
from lms.models.user import User 
import threading

def send_async_email(app, msg):
    """Sends the email asynchronously using a thread."""
    with app.app_context():
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