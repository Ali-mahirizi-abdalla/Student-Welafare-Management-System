import re

path = 'hms/templates/hms/admin/dashboard.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix pattern: {% if/elif ... or\r\n ... %} across lines
# Match {% if/elif ... that doesn't close with %} on the same line, followed by continuation
fixed = re.sub(
    r'(\{%\s*(?:if|elif)\b[^%]*?)\r?\n\s*([^%]*?%\})',
    lambda m: m.group(1).rstrip() + ' ' + m.group(2).lstrip(),
    content
)

count = 0
if fixed != content:
    # Count how many fixes
    orig_lines = content.count('\n')
    new_lines = fixed.count('\n')
    count = orig_lines - new_lines
    with open(path, 'w', encoding='utf-8') as f:
        f.write(fixed)
    print(f"Fixed {count} split tag(s). Lines reduced from {orig_lines+1} to {new_lines+1}.")
else:
    print("No split tags found.")
