# ---------- Stage 1: Build Tailwind CSS ----------
FROM node:20-slim AS css-builder

WORKDIR /build

# Copy Tailwind input CSS
COPY lms/static/css/input.css lms/static/css/input.css

# Copy entire lms folder (templates, JS, CSS, etc.)
COPY lms/ lms/

# Copy Tailwind config
COPY tailwind.config.js ./

# Install Tailwind CLI
RUN npm install -D tailwindcss @tailwindcss/cli

# Build minified Tailwind CSS
RUN npx tailwindcss -i lms/static/css/input.css -o lms/static/css/output.css --minify


# ---------- Stage 2: Python application ----------
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Copy the compiled Tailwind CSS from build stage
COPY --from=css-builder /build/lms/static/css/output.css lms/static/css/output.css

EXPOSE 5000

# Run the app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "--workers", "3", "lms:create_app()"]