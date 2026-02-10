import os
import re

filepath = r'hms/templates/hms/admin/dashboard.html'
if not os.path.exists(filepath):
    print(f"File not found: {filepath}")
    exit(1)

with open(filepath, 'rb') as f:
    data = f.read().decode('utf-8')

original_data = data

# Join split {% ... %} tags
# This regex looks for {% followed by anything (including newlines) until %}
def join_block_tags(match):
    content = match.group(1)
    # Replace newlines and extra spaces with a single space
    joined = re.sub(r'\s+', ' ', content).strip()
    return f'{{% {joined} %}}'

data = re.sub(r'\{%\s*(.*?)\s*%\}', join_block_tags, data, flags=re.DOTALL)

# Join split {{ ... }} tags
def join_var_tags(match):
    content = match.group(1)
    joined = re.sub(r'\s+', ' ', content).strip()
    return f'{{{{ {joined} }}}}'

data = re.sub(r'\{\{\s*(.*?)\s*\}\}', join_var_tags, data, flags=re.DOTALL)

# Ensure the title is correct while we are at it
# (Should already be correct from the last replace_file_content, but better to be safe)
data = data.replace('Kitchen & Admin Dashboard', 'Admin Dashboard')

if data != original_data:
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        f.write(data)
    print("dashboard.html updated successfully with joining regex.")
else:
    print("No changes were made to dashboard.html.")
