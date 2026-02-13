
import re
import os

templates_dir = r'c:\Users\jamal\Downloads\Student-Welfare-Management-System\Student-Welfare-Management-System\hms\templates\hms'

def join_tags(match):
    # Split by any whitespace and join with single spaces
    return ' '.join(match.group(0).split())

def sanitize_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # Process {% ... %} blocks
        content = re.sub(r'\{%.*?%\}', join_tags, content, flags=re.DOTALL)
        # Process {{ ... }} blocks
        content = re.sub(r'\{\{.*?\}\}', join_tags, content, flags=re.DOTALL)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Sanitized: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

for root, dirs, files in os.walk(templates_dir):
    for file in files:
        if file.endswith('.html'):
            sanitize_file(os.path.join(root, file))
