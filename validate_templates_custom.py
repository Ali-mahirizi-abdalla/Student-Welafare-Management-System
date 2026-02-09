import os
import sys
import django
from django.conf import settings
from django.template import Template, TemplateSyntaxError

def run_validation():
    print("Starting validation...")
    
    # Setup Django
    if not settings.configured:
        settings.configure(
            TEMPLATES=[{
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [],
                'APP_DIRS': True,
            }],
            INSTALLED_APPS=[
                'django.contrib.admin',
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.messages',
                'django.contrib.staticfiles',
                'hms',
            ]
        )
        try:
            django.setup()
            print("Django setup completed.")
        except Exception as e:
            print(f"Django setup failed: {e}")
            return

    project_root = os.getcwd()
    print(f"Scanning directory: {project_root}")
    
    report_file = os.path.join(project_root, 'validation_report.txt')
    print(f"Writing report to: {report_file}")
    
    html_files = []
    for root, dirs, files in os.walk(project_root):
        if '.git' in dirs: dirs.remove('.git')
        if 'venv' in dirs: dirs.remove('venv')
        if '__pycache__' in dirs: dirs.remove('__pycache__')
        
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))

    print(f"Found {len(html_files)} HTML files.")

    errors = []
    checked = 0
    
    with open(report_file, 'w', encoding='utf-8') as report:
        report.write("HTML Template Validation Report\n")
        report.write("===============================\n\n")
        
        for file_path in html_files:
            rel_path = os.path.relpath(file_path, project_root)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic Django Template Syntax Check
                try:
                    Template(content)
                    checked += 1
                except TemplateSyntaxError as e:
                    errors.append((rel_path, str(e)))
                    report.write(f"[ERROR] {rel_path}:\n  {e}\n\n")
                    print(f"Error in {rel_path}: {e}")
                except Exception as e:
                    # Catch other potential errors
                    errors.append((rel_path, str(e)))
                    report.write(f"[UNKNOWN ERROR] {rel_path}:\n  {e}\n\n")

            except Exception as e:
                 report.write(f"[FILE READ ERROR] {rel_path}:\n  {e}\n\n")

        summary = f"\nSummary: Checked {checked} files. Found {len(errors)} errors.\n"
        report.write(summary)
        print(summary)

if __name__ == "__main__":
    run_validation()
