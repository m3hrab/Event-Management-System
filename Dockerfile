# Minimal production Dockerfile for Render
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (optional; kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Ensure production env
ENV FLASK_ENV=production

# Expose is optional on Render, but fine
EXPOSE 10000

# Start with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT}", "run:app"]
