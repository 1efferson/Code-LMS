# TODO: Add Course-Specific Real-Time Chat Feature

## 1. Update Dependencies
- [ ] Add Flask-SocketIO to requirements.txt

## 2. Create Message Model
- [ ] Create lms/models/message.py with Message model (id, sender_id, receiver_id, course_id, content, timestamp, read)

## 3. Update Models Import
- [ ] Update lms/models/__init__.py to import Message

## 4. Add Chat Routes
- [ ] Add /course/<course_id>/chat route in lms/instructor/routes.py
- [ ] Add /<course_slug>/chat route in lms/courses/routes.py

## 5. Implement Real-Time Chat
- [ ] Update app.py to initialize SocketIO
- [ ] Add SocketIO events for sending/receiving messages, joining/leaving course rooms

## 6. Create Chat Templates
- [ ] Create lms/instructor/templates/instructor/chat.html (chronological view, highlight unread)
- [ ] Create lms/courses/templates/courses/chat.html (similar)

## 7. Update Existing Templates
- [ ] Add chat link/button in instructor/dashboard.html
- [ ] Add chat link/button in courses/course_details.html or course_lesson.html
- [ ] Add unread badge in main/dashboard.html for students

## 8. Add Notifications
- [ ] Implement in-app badge for unread messages
- [ ] Add optional email notifications for unread messages

## 9. Followup Steps
- [ ] Install dependencies (pip install Flask-SocketIO)
- [ ] Run database migrations (flask db migrate, flask db upgrade)
- [ ] Test chat functionality, permissions, UI
