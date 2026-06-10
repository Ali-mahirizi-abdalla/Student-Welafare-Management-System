import os
import re

def scan_project(root_dir='.'):
    issues_found = []
    
    # Check settings
    settings_path = os.path.join(root_dir, 'swms', 'settings.py')
    if os.path.exists(settings_path):
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'DEBUG = True' in content and 'os.getenv' not in content:
                issues_found.append("[SECURITY] Hardcoded DEBUG = True found in settings.py")
            if 'SECRET_KEY = ' in content and 'os.getenv' not in content and 'config(' not in content:
                issues_found.append("[SECURITY] Hardcoded SECRET_KEY found in settings.py")
    
    # Check templates
    template_dir = os.path.join(root_dir, 'hms', 'templates')
    for subdir, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(subdir, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for missing csrf_token in forms
                    forms = re.findall(r'<form[^>]*method=["\']post["\'][^>]*>(.*?)</form>', content, re.IGNORECASE | re.DOTALL)
                    for form_content in forms:
                        if '{% csrf_token %}' not in form_content:
                            issues_found.append(f"[LOOPHOLE] Missing {{% csrf_token %}} in a POST form in {filepath}")
                    
                    # Check for hardcoded absolute links that might break
                    hardcoded_links = re.findall(r'href=["\'](http://localhost[^"\']*)["\']', content)
                    for link in hardcoded_links:
                        issues_found.append(f"[BROKEN LINK RISK] Hardcoded localhost link found in {filepath}: {link}")

                    # Check for |safe usage which could lead to XSS if user input is rendered
                    if '|safe' in content:
                        issues_found.append(f"[SECURITY] Usage of |safe filter found in {filepath}. Ensure data is sanitized.")

    return issues_found

if __name__ == '__main__':
    print("Starting Security & Link Scan...")
    issues = scan_project()
    if issues:
        print("\n--- ISSUES FOUND ---")
        for issue in issues:
            print(issue)
        print("\nNote: Please review the |safe filter usages to ensure they are not rendering unsanitized user input.")
    else:
        print("No critical loopholes or broken links found.")
