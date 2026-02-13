import re
import os

path = 'hms/templates/hms/admin/dashboard.html'
if not os.path.exists(path):
    print(f"Error: {path} not found.")
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern for split {% ... %} or {{ ... }}
# It looks for opening {{ or {% followed by anything that DOES NOT contain the closing }} or %}
# until it finds the closing one.
def fix_tags(text):
    # Fix {% ... %}
    text = re.sub(r'(\{%\s*[^%]*?)\r?\n\s*([^%]*?%\})', r'\1 \2', text)
    # Fix {{ ... }}
    text = re.sub(r'(\{\{\s*[^}]*?)\r?\n\s*([^}]*?\}\})', r'\1 \2', text)
    return text

fixed = content
# Run multiple times to catch tags split over more than 2 lines (though rare)
for _ in range(3):
    fixed = fix_tags(fixed)

if fixed != content:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(fixed)
    print("Fixed split tags.")
else:
    print("No split tags found.")
