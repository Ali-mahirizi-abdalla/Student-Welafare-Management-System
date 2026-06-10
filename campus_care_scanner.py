import os
import re

def check_security_and_links(base_dir):
    issues = []
    
    print("=======================================")
    print(" Campus Care Scanner - Security & Links")
    print("=======================================\n")
    
    # 1. Check Settings.py
    settings_path = os.path.join(base_dir, 'swms', 'settings.py')
    if os.path.exists(settings_path):
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "DEBUG = True" in content and "os.environ" not in content and "os.getenv" not in content:
                issues.append(("[SECURITY]", "settings.py has hardcoded DEBUG=True"))
            if "SECRET_KEY = " in content and "os.environ" not in content and "os.getenv" not in content:
                issues.append(("[SECURITY]", "settings.py has hardcoded SECRET_KEY"))
            
    # 2. Check Templates for CSRF and Broken Links
    templates_dir = os.path.join(base_dir, 'hms', 'templates')
    static_dir = os.path.join(base_dir, 'hms', 'static')
    
    if os.path.exists(templates_dir):
        for root, dirs, files in os.walk(templates_dir):
            for file in files:
                if file.endswith('.html'):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Check CSRF
                        forms = re.findall(r'<form[^>]*method=["\']post["\'][^>]*>(.*?)</form>', content, re.IGNORECASE | re.DOTALL)
                        for form in forms:
                            if '{% csrf_token %}' not in form and '{{ csrf_token }}' not in form:
                                issues.append(("[LOOPHOLE]", f"Missing CSRF token in POST form in {os.path.relpath(filepath, base_dir)}"))
                                
                        # Check |safe filter usage
                        if '|safe' in content:
                            issues.append(("[WARNING]", f"Usage of |safe filter found in {os.path.relpath(filepath, base_dir)}. Ensure variables are sanitized."))
                            
                        # Check for hardcoded localhost URLs
                        if 'http://localhost' in content or 'http://127.0.0.1' in content:
                            issues.append(("[BROKEN LINK RISK]", f"Hardcoded localhost URL found in {os.path.relpath(filepath, base_dir)}"))

                        # Check for static links that might be broken
                        static_tags = re.findall(r'{%\s*static\s+["\']([^"\']+)["\']\s*%}', content)
                        for static_file in static_tags:
                            static_filepath = os.path.join(static_dir, static_file.replace('/', os.sep))
                            if not os.path.exists(static_filepath):
                                issues.append(("[BROKEN LINK]", f"Missing static file '{static_file}' referenced in {os.path.relpath(filepath, base_dir)}"))
                                
    if not issues:
        print("[OK] Awesome! No major security loopholes or broken link risks found.")
        print("The system's settings correctly rely on environment variables for production.")
    else:
        print(f"[!] Found {len(issues)} potential issue(s):\n")
        for issue_type, desc in issues:
            print(f"{issue_type:<20} {desc}")
            
    print("\nScan completed.")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    check_security_and_links(base_dir)
