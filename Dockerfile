# Use a lightweight Python base image
FROM python:3.13-slim

# Avoid Python writing .pyc files and ensure output is logged straight
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Install Node so Tailwind CLI can run
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean

# Install Python dependencies first (caching optimization)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Install Tailwind CLI and build CSS
RUN npm install -D tailwindcss @tailwindcss/cli
RUN npx @tailwindcss/cli -i lms/static/css/input.css -o lms/static/css/output.css --minify

# Expose port
EXPOSE 5000

# Start Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "lms:create_app()"]
