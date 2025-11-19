from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from flask import request
from lms import socketio, db
from lms.models import Message, Course, Enrollment
import datetime

@socketio.on('join_course_chat')
def handle_join_course_chat(data):
    course_id = data['course_id']
    receiver_id = data.get('receiver_id')  # For private chats
    course = Course.query.get(course_id)
    if not course:
        emit('error', {'message': 'Course not found'})
        return

    # Check permissions: enrolled student or instructor
    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    if not enrollment and course.instructor_id != current_user.id:
        emit('error', {'message': 'Permission denied'})
        return

    if receiver_id:
        # Join private room
        join_room(f'course_{course_id}_private_{receiver_id}')
    else:
        join_room(f'course_{course_id}')
    emit('joined', {'message': f'Joined chat for {course.title}'})


@socketio.on('leave_course_chat')
def handle_leave_course_chat(data):
    course_id = data['course_id']
    leave_room(f'course_{course_id}')
    emit('left', {'message': f'Left chat for course {course_id}'})


@socketio.on('send_message')
def handle_send_message(data):
    course_id = data['course_id']
    content = data['content'].strip()
    if not content:
        return

    course = Course.query.get(course_id)
    if not course:
        emit('error', {'message': 'Course not found'})
        return

    # Check permissions
    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    if not enrollment and course.instructor_id != current_user.id:
        emit('error', {'message': 'Permission denied'})
        return

    # Determine receivers
    if 'receiver_id' in data:
        receivers = [data['receiver_id']]
    elif current_user.id == course.instructor_id:
        receivers = [e.user_id for e in course.enrollments]
    else:
        receivers = [course.instructor_id]

    for receiver_id in receivers:
        message = Message(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            course_id=course_id,
            content=content,
            timestamp=datetime.datetime.utcnow(),
            read=False
        )
        db.session.add(message)

    db.session.commit()

    # Emit to general room always
    emit('new_message', {
        'sender_name': current_user.name,
        'content': content,
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'course_id': course_id
    }, room=f'course_{course_id}')
