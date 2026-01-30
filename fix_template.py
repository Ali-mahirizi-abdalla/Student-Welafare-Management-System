#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix template rendering issues in deferment_list.html"""

import re

file_path = r'c:\Users\jamal\Downloads\Student-Welfare-Management-System\Student-Welfare-Management-System\hms\templates\hms\admin\deferment_list.html'

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix split template variables
fixes = [
    # Fix student name
    (r'{{\s*\r?\n\s*deferment\.student\.user\.get_full_name\s*}}', '{{ deferment.student.user.get_full_name }}'),
    # Fix university ID
    (r'{{\s*deferment\.student\.university_id\s*\r?\n\s*}}', '{{ deferment.student.university_id }}'),
    # Fix end date
    (r'{{\s*\r?\n\s*deferment\.end_date\|date:"M d, Y"\s*}}', '{{ deferment.end_date|date:"M d, Y" }}'),
]

for pattern, replacement in fixes:
    content = re.sub(pattern, replacement, content)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Template fixed successfully!")
