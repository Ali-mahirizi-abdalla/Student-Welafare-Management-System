# +++++++++++ DJANGO WSGI CONFIGURATION FOR PYTHONANYWHERE +++++++++++
# This file contains the WSGI configuration required to serve up your
# web application on PythonAnywhere.
# It works by setting the variable 'application' to a WSGI handler of some
# description.

import os
import sys

# Add your project directory to the sys.path
project_home = '/home/yourusername/Student-Welfare-Management-System/Student-Welfare-Management-System'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables from .env file
from pathlib import Path
env_file = Path(project_home) / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swms.settings')

# Import Django's WSGI handler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
