# Use Python 3.12 slim image for smaller size
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    FLASK_ENV=production \
    FLASK_APP=run.py

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r flaskuser && useradd -r -g flaskuser flaskuser

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM base as production

# Copy application code
COPY --chown=flaskuser:flaskuser . .

# Create instance directory for Flask
RUN mkdir -p instance && chown -R flaskuser:flaskuser instance

# Switch to non-root user
USER flaskuser

# Expose port
EXPOSE 5001

# Start with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "1", "--threads", "1", "run:app"]
