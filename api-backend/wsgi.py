"""
Standalone WSGI entry point for the Flask application.
This file should NOT use relative imports as it's outside the package.
This file must expose a variable named 'app' that is a WSGI application.
"""
import os
import sys

# Ensure the current directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Print current working directory and Python path for debugging
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Import the create_app function from app.py
from app import create_app

# Create the Flask application instance that Gunicorn will use
# This must be named 'app' for Gunicorn to find it
app = create_app()
print("Created Flask app instance successfully")

# For direct execution
if __name__ == "__main__":
    # This block only runs when wsgi.py is directly executed, not via Gunicorn
    app.run(host="0.0.0.0", port=8000)
