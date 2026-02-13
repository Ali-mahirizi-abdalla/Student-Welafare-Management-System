import re
import os

templates_dir = r'c:\Users\jamal\Downloads\Student-Welfare-Management-System\Student-Welfare-Management-System\hms\templates\hms'

def normalize_tag(match):
    tag = match.group(0)
    # Join multiline tags
    tag = ' '.join(tag.split())
    # Ensure spaces around operators
    if tag.startswith('{% if') or tag.startswith('{% elif'):
        # Add spaces around ==
        tag = re.sub(r'([^ ])==', r'\1 ==', tag)
        tag = re.sub(r'==([^ ])', r'== \1', tag)
        # Add spaces around !=
        tag = re.sub(r'([^ ])!=', r'\1 !=', tag)
        tag = re.sub(r'!=([^ ])', r'!= \1', tag)
        # Add spaces around <= and >=
        tag = re.sub(r'([^ ])>=', r'\1 >=', tag)
        tag = re.sub(r'>=([^ ])', r'>= \1', tag)
        tag = re.sub(r'([^ ])<=', r'\1 <=', tag)
        tag = re.sub(r'<=([^ ])', r'<= \1', tag)
        # Cleanup double spaces
        tag = ' '.join(tag.split())
    return tag

def sanitize_file(file_path):
    try:
        if not os.path.isfile(file_path):
            return
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # Join split {% ... %} tags and normalize
        content = re.sub(r'\{%.*?%\}', normalize_tag, content, flags=re.DOTALL)
        # Join split {{ ... }} tags
        content = re.sub(r'\{\{.*?\}\}', lambda m: ' '.join(m.group(0).split()), content, flags=re.DOTALL)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Sanitized: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                sanitize_file(os.path.join(root, file))
    print("Template Sanitization and Normalization Complete.")
