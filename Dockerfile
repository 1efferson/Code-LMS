# Use a lightweight Python base image
FROM python:3.13-slim

# Avoid Python writing .pyc files and ensure output is logged straight
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create working directory
WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . .

# Expose the port gunicorn will serve on
EXPOSE 5000

# Gunicorn runs the Flask app factory
CMD ["gunicorn", "-b", "0.0.0.0:5000", "lms:create_app()"]
