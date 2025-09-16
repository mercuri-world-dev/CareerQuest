# Multi-stage, installs Node deps for static folder and Python deps for the app.
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    FLASK_ENV=production \
    FLASK_APP=run.py

# Install system utilities and Node.js (single apt run)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates curl gnupg build-essential && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# Set workdir early so subsequent COPY paths are relative to /app
WORKDIR /app

# Copy only files needed for dependency installation to leverage Docker cache
#  - Python requirements
COPY requirements.txt .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy node package metadata from the static folder (if present) to allow npm ci caching
# If you use package-lock.json in static, copy it as well for deterministic installs.
COPY static/package.json static/package-lock.json* ./static/

# Install static (node) dependencies inside /app/static
RUN if [ -d "./static" ]; then cd static && npm ci --production; fi

# Copy the rest of application code
COPY . .

# Create non-root user and set ownership of instance and static folders
RUN groupadd -r flaskuser && useradd -r -g flaskuser flaskuser && \
    mkdir -p instance && chown -R flaskuser:flaskuser instance static

# Switch to non-root user
USER flaskuser

EXPOSE 5001

# Use gunicorn in production; adjust workers/threads as needed
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "1", "--threads", "1", "run:app"]