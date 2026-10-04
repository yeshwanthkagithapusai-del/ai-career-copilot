#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Building AI Career Copilot..."

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate --no-input

# Collect static files
python manage.py collectstatic --no-input

echo "Build complete."
