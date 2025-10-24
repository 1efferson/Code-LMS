# 🚀 Code-LMS: A Modern, Modular Learning Management System

**Code-LMS** is a modern, modular Learning Management System built with the Flask micro-framework.  
It’s designed to deliver structured educational content, primarily focused on **computer science and programming**.

The system features a multi-level course catalog, secure enrollment, and an immersive video lesson player inspired by platforms like YouTube.  
The goal is to create a **clean, scalable platform** for both students and administrators to manage learning and course delivery effectively.

---

## ✨ Key Features

- **Three-Tier Course Structure** — Courses are categorized into **Beginner**, **Intermediate**, and **Advanced** levels for a clear learning pathway.  
- **Immersive Lesson Viewer** — Two-column layout featuring a large video player and a persistent course playlist.  
- **Secure Enrollment Logic** — Only enrolled and authenticated users can access course content.  
- **Modern UI/UX** — Built with **Tailwind CSS** **plain css** and **Jinja2** for a responsive, visually appealing interface.  
- **Modular Architecture** — Organized using Flask **Blueprints** for clean, scalable code management.

---

## 💻 Tech Stack

| Category | Technology | Purpose |
|-----------|-------------|----------|
| **Backend** | Python 3 | Core programming language |
| **Web Framework** | Flask | Lightweight web framework |
| **Database** | SQLAlchemy | ORM for database modeling |
| **Frontend** | Jinja2 | Dynamic HTML templating |
| **Styling** | Tailwind CSS | Utility-first CSS framework |
| **Authentication** | Flask-Login | Session management and user control |
| **Security** | Flask-Bcrypt | Secure password hashing |

---

## ⚙️ Getting Started

Follow these steps to set up **Code-LMS** locally.

### 1. Clone the Repository
  ```bash
        git clone [YOUR_REPOSITORY_URL]
        cd code-lms
```

###  2. Setup Virtual Environment

   ```bash
        Setup Virtual Environment
        python -m venv venv
        # Activate the environment (Linux/macOS)
        source venv/bin/activate
        # Activate the environment (Windows)
        .\venv\Scripts\activate
   ```

### 3. Install Dependencies
   ```bash 
    pip install -r requirements.txt
 ```


### 4. Configure Environment Variables
Create a .env and flaskenv file respectively in the root directory and add:
```bash 
   SECRET_KEY="YOUR_SUPER_SECRET_KEY_HERE"
  SQLALCHEMY_DATABASE_URI="sqlite:///site.db"
 
 ```
```bash 
   FLASK_APP=run.py
  FLASK_ENV=development
 
 ```

###  5. Initialize the Database using Flask-Migrate:

```bash 
 flask db upgrade

 ```
### 6. Run the Application
```bash 
 flask run

 ```

## 🧩 Architecture & Blueprints

The system is modular, using Flask Blueprints for clear separation of features.

### **main Blueprint**
Handles general pages and non-core routes.

| Route | Purpose | Access | Template |
|-------|----------|--------|-----------|
| `/` | Homepage | Public | `home.html` |
| `/about` | Info about the LMS | Public | `about.html` |
| `/dashboard` | User dashboard | Logged In | `dashboard.html` |

---

### **auth Blueprint**
Manages authentication and session handling via Flask-Login.

| Route | Purpose | Access | Template |
|-------|----------|--------|-----------|
| `/register` | User registration | Public | `auth/register.html` |
| `/login` | User login | Public | `auth/login.html` |
| `/logout` | Logout and redirect | Logged In | Redirects |

---

### **courses Blueprint**
Handles the core course logic — catalog, enrollment, and lessons.

| Route | Purpose | Access | Template |
|-------|----------|--------|-----------|
| `/courses` | Course catalog | Public | `courses/course_catalog.html` |
| `/enroll/<slug>` | Enroll user in course | Logged In (POST) | Redirect to first lesson |
| `/<course_slug>/<lesson_slug>` | Lesson viewer | Enrolled users | `courses/course_lesson.html` |

---

## 🧱 Database Models

The app uses SQLAlchemy ORM to manage relationships between entities.

| Model | Description |
|--------|-------------|
| **User** | Stores user credentials and integrates with Flask-Login |
| **Course** | Contains metadata like title, slug, level, and description |
| **Module** | Organizes lessons within a course (e.g., “Introduction to Python”) |
| **Lesson** | The core content unit — includes title, slug, and video embed URL |
| **Enrollment** | Many-to-many relationship linking Users and Courses |
| **Progress (In progress)** | Tracks lesson completion for each user |



## Roadmap
   **Add progress tracking and completion certificates**
    
   **Build an admin dashboard for instructors**
    
   **Add comments/discussions to lessons**
    
   **Analytics dashboard for student performance**


## Authors

  ** Jeph Ampadu**
  ** Jude tetteh-Fio**

## License

  **This project is licensed under the MIT License.**

