import re

path = 'hms/templates/hms/admin/dashboard.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'{%\s*(if|endif|for|endfor|block|endblock|elif|else)\b.*?%}'
stack = []
mapping = {'endif': 'if', 'endfor': 'for', 'endblock': 'block'}

for m in re.finditer(pattern, content):
    tag_type = m.group(1)
    line = content[:m.start()].count('\n') + 1
    if tag_type in ('if', 'for', 'block'):
        stack.append((tag_type, line))
    elif tag_type in mapping:
        expected = mapping[tag_type]
        if not stack:
            print(f"ERR L{line}: unmatched {tag_type}")
        else:
            top_type, top_line = stack.pop()
            if top_type != expected:
                print(f"ERR L{line}: {tag_type} closes {top_type}@L{top_line}")

for t, l in stack:
    print(f"ERR: unclosed {t}@L{l}")

if not stack:
    print("OK")
