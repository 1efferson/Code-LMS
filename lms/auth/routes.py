# lms/auth/routes.py

from flask import render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from lms import db, bcrypt
from lms.models import User
from .forms import RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from . import auth
from lms.utils import send_reset_email


# ---------------------------
# Registration route
# ---------------------------
@auth.route('/register', methods=['GET', 'POST'])
def register():
    # Redirect to courses page if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('courses.index'))

    form = RegisterForm()
    # Check if form was submitted and passed validation
    if form.validate_on_submit():
        # Hash the password for security
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Check if user entered the correct admin signup code
        is_admin_user = (form.admin_code.data == current_app.config.get('ADMIN_SIGNUP_CODE'))
        
        # Assign role based on admin code
        role = 'admin' if is_admin_user else 'student'

        # Create new user record
        user = User(
            name=form.name.data, 
            email=form.email.data, 
            password=hashed_pw, 
            role=role,
            is_admin=is_admin_user 
        )
        
        # Add and commit new user to database
        db.session.add(user)
        db.session.commit()

        # Notify user and log them in
        flash(f'Account created for {form.name.data} as {role}!', 'success')
        login_user(user)
        current_app.logger.debug("login_user called for id=%s; session keys=%s", user.id, list(session.keys()))

        # Redirect to main course page
        return redirect(url_for('courses.index'))

    # Render registration page with form
    return render_template('auth/register.html', form=form)


# ---------------------------
# Login route
# ---------------------------
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('courses.index'))

    form = LoginForm()
    if form.validate_on_submit():
        # Look up user by email
        user = User.query.filter_by(email=form.email.data).first()
        
        # Verify credentials
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            current_app.logger.debug("login_user called for id=%s; session keys=%s", user.id, list(session.keys()))
            flash('Login successful!', 'success')

            # Redirect to next page if available, else to course index
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('courses.index'))
        else:
            # Display invalid credentials message
            flash('Invalid email or password.', 'danger')

    # Render login page with form
    return render_template('auth/login.html', form=form)


# ---------------------------
# Logout route
# ---------------------------
@auth.route('/logout')
@login_required
def logout():
    # Log out the current user
    logout_user()
    flash('You have been logged out.', 'info')

    # Redirect to login or provided next page
    next_page = request.args.get('next')
    if next_page and next_page.startswith('/'):
        return redirect(next_page)

    return redirect(url_for('auth.login'))


# ---------------------------
# Forgot password route (initiates reset)
# ---------------------------
@auth.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    # Logged-in users don't need to reset their password
    if current_user.is_authenticated:
        return redirect(url_for('main.home')) 
    
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        # Find user by email
        user = User.query.filter_by(email=form.email.data).first()
        
        # If user exists, send reset email
        if user:
            send_reset_email(user)
        
        # Always show same message to prevent info leaks
        flash("If an account with that email address exists, you will receive an email with instructions to reset your password.", "info")
        return redirect(url_for("auth.login"))

    # Render forgot password form
    return render_template("auth/forgot_password.html", form=form, title='Forgot Password')


# ---------------------------
# Reset password route (handles reset token)
# ---------------------------
@auth.route("/reset_password/<string:token>", methods=['GET', 'POST'])
def reset_token(token):
    # Skip reset if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.home')) 

    # Verify the reset token
    user = User.verify_reset_token(token) 
    
    if user is None:
        # Token invalid or expired
        flash('That is an invalid or expired token. Please try resetting your password again.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        # Hash and update the user's new password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password_hash = hashed_password
        db.session.commit()
        
        # Notify success and redirect to login
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    # Render password reset form
    return render_template('auth/reset_password.html', title='Reset Password', form=form)
