path = 'hms/templates/hms/admin/dashboard.html'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Print lines 128-131 (0-indexed 127-130)
for i in range(127, 131):
    line = lines[i]
    has_if = '{%' in line and 'if' in line
    has_percent_close = '%}' in line
    print(f"L{i+1} has_if={has_if} has_close={has_percent_close}: {repr(line[:120])}")
