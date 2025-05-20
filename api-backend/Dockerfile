FROM python:3.13-slim

WORKDIR /app

# Copy package definition files first
COPY pyproject.toml .
COPY README.md .

# Install the package in development mode so source changes are reflected
RUN pip install --no-cache-dir -e .

# Copy the rest of the files
COPY . .

EXPOSE 8000

# Use wsgi.py which imports from app.py to run the application with clear path and module name
# Log to stdout, use a single worker, and specify a timeout for debugging
CMD ["gunicorn", "wsgi:app", "--workers", "1", "--bind", "0.0.0.0:8000", "--log-level", "debug", "--timeout", "120"]