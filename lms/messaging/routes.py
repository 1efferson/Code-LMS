# lms/messaging/routes.py
# TWO-WAY MESSAGING VERSION
# Both instructors and students can send messages

from flask import render_template, request, jsonify, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from lms.extensions import db
from lms.models import User, Message
from .forms import SendMessageForm, MarkAsReadForm
from . import messaging


# =====================================================
# AUTHORIZATION HELPERS
# =====================================================

def is_instructor():
    """Check if current user is an instructor."""
    return current_user.is_authenticated and current_user.role == 'instructor'


def is_student():
    """Check if current user is a student."""
    return current_user.is_authenticated and current_user.role == 'student'


def can_message_student(student_id):
    """
    Check if current instructor can message this student.
    Instructor can message students enrolled in their courses.
    """
    if not is_instructor():
        return False
    
    student = User.query.get(student_id)
    if not student or student.role != 'student':
        return False
    
    # Check if student is enrolled in any of instructor's courses
    from lms.models import Course, Enrollment
    
    instructor_courses = Course.query.filter_by(instructor_id=current_user.id).all()
    course_ids = [course.id for course in instructor_courses]
    
    enrolled = Enrollment.query.filter(
        and_(
            Enrollment.user_id == student_id,
            Enrollment.course_id.in_(course_ids)
        )
    ).first()
    
    return enrolled is not None


# =====================================================
# SEND MESSAGE (AJAX) - TWO-WAY VERSION
# =====================================================

@messaging.route('/send', methods=['POST'])
@login_required
def send_message():
    """
    Send a message (TWO-WAY: instructor → student OR student → instructor).
    """
    
    form = SendMessageForm()
    
    if form.validate_on_submit():
        receiver_id = int(form.receiver_id.data)
        receiver = User.query.get_or_404(receiver_id)
        
        # ===== AUTHORIZATION LOGIC (TWO-WAY) =====
        if is_instructor():
            if not can_message_student(receiver_id):
                return jsonify({
                    'success': False,
                    'error': 'You can only message students enrolled in your courses'
                }), 403
        
        elif is_student():
            if receiver.role != 'instructor':
                return jsonify({
                    'success': False,
                    'error': 'You can only message instructors'
                }), 403
            
            prior_message = Message.query.filter(
                and_(
                    Message.sender_id == receiver_id,
                    Message.receiver_id == current_user.id
                )
            ).first()
            
            if not prior_message:
                return jsonify({
                    'success': False,
                    'error': 'You can only reply to instructors who have messaged you first'
                }), 403
        
        else:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # ===== CREATE MESSAGE =====
        try:
            message = Message(
                sender_id=current_user.id,
                receiver_id=receiver_id,
                subject=form.subject.data or None,
                content=form.content.data.strip(),
                is_read=False
            )
            
            db.session.add(message)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Message sent successfully!',
                'receiver_id': receiver_id,  # ✅ Include this
                'data': {
                    'id': message.id,
                    'created_at': message.time_ago()
                }
            }), 200
            
        except Exception:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Failed to send message. Please try again.'
            }), 500
    
    # Form validation failed
    errors = {field: errs[0] for field, errs in form.errors.items()}
    return jsonify({'success': False, 'errors': errors}), 400




# =====================================================
# VIEW CONVERSATION - TWO-WAY VERSION
# =====================================================

@messaging.route('/conversation/<int:user_id>')
@login_required
def conversation(user_id):
    """
    View conversation between current user and another user.
    TWO-WAY: Works for instructor→student AND student→instructor.
    
    Security:
    - Instructors can view conversations with their students
    - Students can view conversations with instructors who messaged them

    """
    print("Conversation access:",
      "current_user =", current_user.id,
      "other_user =", user_id,
      "role =", current_user.role)
    
    other_user = User.query.get_or_404(user_id)
    
    # ===== AUTHORIZATION (TWO-WAY) =====
    if is_instructor():
        has_conversation = Message.query.filter(
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
                and_(Message.sender_id == user_id, Message.receiver_id == current_user.id)
            )
        ).first()

        if not has_conversation and not can_message_student(user_id):
            abort(403)
    
    elif is_student():
        # Student viewing conversation with instructor
        
        # Check 1: Other user must be an instructor
        if other_user.role != 'instructor':
            abort(403)
        
        # Check 2: Must have an existing conversation
        has_conversation = Message.query.filter(
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
                and_(Message.sender_id == user_id, Message.receiver_id == current_user.id)
            )
        ).first()
        
        if not has_conversation:
            abort(403)
    
    else:
        abort(403)
        
    
    # ===== GET MESSAGES =====
    
    # Get all messages in conversation (both directions)
    messages = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
            and_(Message.sender_id == user_id, Message.receiver_id == current_user.id)
        ),
        Message.is_deleted == False
    ).order_by(Message.created_at.asc()).all()
    
    # Mark received messages as read
    for msg in messages:
        if msg.receiver_id == current_user.id and not msg.is_read:
            msg.mark_as_read()
    
    # ===== PREPARE FORM =====
    
    form = SendMessageForm()
    form.receiver_id.data = user_id
    
    return render_template(
        'messaging/conversation.html',
        messages=messages,
        other_user=other_user,
        form=form
    )



# =====================================================
# INBOX (STUDENT VIEW)
# =====================================================

@messaging.route('/inbox')
@login_required
def inbox():
    """
    Student inbox - view all received messages.
    
    Security:
    - Only students can access inbox
    - Users can only see their own messages
    """
    
    if not is_student():
        flash('Only students can access the inbox.', 'warning')
        return redirect(url_for('courses.index'))
    
    # Get all messages for current student
    messages = Message.query.filter_by(
        receiver_id=current_user.id,
        is_deleted=False
    ).order_by(Message.created_at.desc()).all()
    
    # Count unread messages
    unread_count = Message.query.filter_by(
        receiver_id=current_user.id,
        is_read=False,
        is_deleted=False
    ).count()
    
    return render_template(
        'messaging/inbox.html',
        messages=messages,
        unread_count=unread_count
    )


# =====================================================
# MARK AS READ (AJAX)
# =====================================================

@messaging.route('/mark-read/<int:message_id>', methods=['POST'])
@login_required
def mark_as_read(message_id):
    """
    Mark a message as read (AJAX endpoint).
    
    Security:
    - Only message receiver can mark as read
    - CSRF protected
    """
    
    message = Message.query.get_or_404(message_id)
    
    # Only the receiver can mark as read
    if message.receiver_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        message.mark_as_read()
        return jsonify({'success': True, 'message': 'Message marked as read'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to mark as read'}), 500


# =====================================================
# GET UNREAD COUNT (AJAX)
# =====================================================

@messaging.route('/unread-count', methods=['GET'])
@login_required
def unread_count():
    """
    Get count of unread messages for current user (for badge display).
    """
    
    if is_student():
        count = Message.query.filter_by(
            receiver_id=current_user.id,
            is_read=False,
            is_deleted=False
        ).count()
    else:
        count = 0
    
    return jsonify({'success': True, 'count': count}), 200


# =====================================================
# DELETE MESSAGE (SOFT DELETE)
# =====================================================

@messaging.route('/delete/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    """
    Soft delete a message (keeps in database for audit).
    
    Security:
    - Only sender or receiver can delete
    - CSRF protected
    """
    
    message = Message.query.get_or_404(message_id)
    
    # Only sender or receiver can delete
    if message.sender_id != current_user.id and message.receiver_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        message.soft_delete()
        return jsonify({'success': True, 'message': 'Message deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to delete message'}), 500