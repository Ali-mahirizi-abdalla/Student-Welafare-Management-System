import os

for root, dirs, files in os.walk('.'):
    if 'venv' in root or '.git' in root or '__pycache__' in root:
        continue
    for f in files:
        if f.endswith('.html'):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read().lower()
                    if '<form' in content and 'method="post"' in content and 'csrf_token' not in content:
                        print(f"Missing CSRF token in: {path}")
            except Exception as e:
                pass
