import re
import os

path = r'c:\Users\jamal\Downloads\Student-Welfare-Management-System\Student-Welfare-Management-System\hms\templates\hms\includes\sidebar.html'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

def fix_tags(text):
    # Fix {% ... %} split across lines
    # This regex looks for {% followed by any characters (non-greedy) until %}
    # If there's a newline in between, it replaces it with a space.
    def replace_tag(match):
        return match.group(0).replace('\r\n', ' ').replace('\n', ' ')
    
    # We want to match {% ... %} but only if there is a newline inside.
    # [^%] for {% tags
    fixed = re.sub(r'\{%.*?%\}', replace_tag, text, flags=re.DOTALL)
    fixed = re.sub(r'\{\{.*?\}\}', replace_tag, fixed, flags=re.DOTALL)
    
    # Also clean up multiple spaces introduced
    fixed = re.sub(r'([ ]{2,})', ' ', fixed) # This might mess with indentation if not careful.
    # Better: only clean spaces INSIDE tags.
    
    def clean_inside(match):
        tag = match.group(0)
        # remove multiple spaces inside tags
        return re.sub(r'\s+', ' ', tag)

    fixed = re.sub(r'\{%.*?%\}', clean_inside, text, flags=re.DOTALL)
    fixed = re.sub(r'\{\{.*?\}\}', clean_inside, fixed, flags=re.DOTALL)
    
    return fixed

fixed = fix_tags(content)

if fixed != content:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(fixed)
    print("Fixed split tags in sidebar.html")
else:
    print("No split tags fixed.")
