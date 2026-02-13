
import re
import os

file_path = r'c:\Users\jamal\Downloads\Student-Welfare-Management-System\Student-Welfare-Management-System\hms\templates\hms\admin\dashboard.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

def join_tags(match):
    # Split by any whitespace and join with single spaces
    return ' '.join(match.group(0).split())

# Process {% ... %} blocks
content = re.sub(r'\{%.*?%\}', join_tags, content, flags=re.DOTALL)

# Process {{ ... }} blocks
content = re.sub(r'\{\{.*?\}\}', join_tags, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Aggressively sanitized {file_path}")
