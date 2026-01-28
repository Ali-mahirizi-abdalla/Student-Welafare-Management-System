"""
Script to bulk update template files with SWMS branding
Replaces all occurrences of HMS/Hostel with SWMS branding
"""
import os
import re

# Define the templates directory
TEMPLATES_DIR = r'c:\Users\jamal\Downloads\Student-Welfare-Management-System\Student-Welfare-Management-System\hms\templates\hms'

# Define replacement patterns
REPLACEMENTS = [
    # Title blocks
    (r'{% block title %}(.+?)-\s*HMS', r'{% block title %}\1- SWMS'),
    (r'{% block title %}HMS\s*-\s*(.+?){% endblock %}', r'{% block title %}SWMS - \1{% endblock %}'),
    
    # Text content
    ('Hostel Management System', 'Student Welfare Management System'),
    ('hostel management', 'student welfare'),
    ('HMS Portal', 'SWMS Portal'),
    
    # Meta tags
    ('content="HMS -', 'content="SWMS -'),
    ('content="Hostel Management', 'content="Student Welfare Management'),
]

def update_template(file_path):
    """Update a single template file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all replacements
        for old, new in REPLACEMENTS:
            if old.startswith('r\''):  # Regex pattern
                content = re.sub(old, new, content)
            else:  # Simple string replacement
                content = content.replace(old, new)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return None

def main():
    """Main function to update all templates"""
    updated_files = []
    unchanged_files = []
    errors = []
    
    # Walk through all HTML files
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                result = update_template(file_path)
                
                if result is True:
                    updated_files.append(file_path)
                elif result is False:
                    unchanged_files.append(file_path)
                else:
                    errors.append(file_path)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"SWMS BRANDING UPDATE SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Updated: {len(updated_files)} files")
    print(f"⚪ Unchanged: {len(unchanged_files)} files")
    print(f"❌ Errors: {len(errors)} files")
    print(f"{'='*60}\n")
    
    if updated_files:
        print("Updated files:")
        for f in updated_files:
            print(f"  - {os.path.basename(f)}")
    
    if errors:
        print("\nFiles with errors:")
        for f in errors:
            print(f"  - {os.path.basename(f)}")

if __name__ == '__main__':
    main()
