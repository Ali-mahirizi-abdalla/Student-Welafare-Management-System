import re

path = 'hms/templates/hms/admin/dashboard.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find ALL template tags with their positions
pattern = r'{%\s*(if|endif|for|endfor|block|endblock|elif|else)\b.*?%}'
stack = []
errors = []
mapping = {'endif': 'if', 'endfor': 'for', 'endblock': 'block'}

for m in re.finditer(pattern, content):
    tag_text = m.group(0)
    tag_type = m.group(1)
    line_num = content[:m.start()].count('\n') + 1

    if tag_type in ('if', 'for', 'block'):
        stack.append((tag_type, tag_text[:60], line_num))
    elif tag_type in mapping:
        expected = mapping[tag_type]
        if not stack:
            errors.append(f"L{line_num}: Unmatched {tag_text[:60]}")
        else:
            top = stack.pop()
            if top[0] != expected:
                errors.append(f"L{line_num}: '{tag_type}' closes '{top[0]}' from L{top[2]} ({top[1]})")
    elif tag_type in ('elif', 'else'):
        if not stack or stack[-1][0] != 'if':
            errors.append(f"L{line_num}: Orphaned {tag_text[:60]}")

for item in stack:
    errors.append(f"Unclosed '{item[0]}' from L{item[2]}: {item[1]}")

if errors:
    for e in errors:
        print(e)
else:
    print("ALL TAGS MATCHED!")
