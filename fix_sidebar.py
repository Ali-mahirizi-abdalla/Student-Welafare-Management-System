
import os

file_path = r'c:\Users\jamal\Downloads\Student-Welfare-Management-System\Student-Welfare-Management-System\hms\templates\hms\includes\sidebar.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_next = False

for i in range(len(lines)):
    if skip_next:
        skip_next = False
        continue
    
    current_line = lines[i].rstrip()
    if current_line.endswith('or') or current_line.endswith('else'):
        if i + 1 < len(lines):
            next_line = lines[i+1].lstrip()
            new_lines.append(current_line + ' ' + next_line)
            skip_next = True
        else:
            new_lines.append(current_line + '\n')
    else:
        new_lines.append(lines[i])

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Successfully processed {file_path}")
