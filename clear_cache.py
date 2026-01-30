import os
import shutil

# Clear Django's template cache
cache_dirs = [
    '__pycache__',
    'hms/__pycache__',
    'swms/__pycache__',
]

for cache_dir in cache_dirs:
    if os.path.exists(cache_dir):
        try:
            shutil.rmtree(cache_dir)
            print(f"Cleared: {cache_dir}")
        except Exception as e:
            print(f"Could not clear {cache_dir}: {e}")

print("\nTemplate cache cleared. Please restart the server manually with Ctrl+C then run again:")
print("python manage.py runserver 127.0.0.1:8000 --skip-checks")
