# Use a lightweight Python base image
FROM python:3.13-slim

# Set environment variables for Flask
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=lms:create_app \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_ENV=development

# Create and set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the entire project into the image
COPY . .

# Expose port Flask runs on
EXPOSE 5000

# Default command to run the app
CMD ["flask", "run"]
