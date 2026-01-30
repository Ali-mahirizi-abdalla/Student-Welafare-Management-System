#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix template rendering issues in multiple admin templates"""

import re
import os

# Define files to fix
files_to_fix = [
    r'c:\Users\jamal\Downloads\Student-Welfare-Management-System\Student-Welfare-Management-System\hms\templates\hms\admin\review_deferment.html',
    r'c:\Users\jamal\Downloads\Student-Welfare-Management-System\Student-Welfare-Management-System\hms\templates\hms\admin\approve_leave.html',
    r'c:\Users\jamal\Downloads\Student-Welfare-Management-System\Student-Welfare-Management-System\hms\templates\hms\admin\leave_requests.html',
    r'c:\Users\jamal\Downloads\Student-Welfare-Management-System\Student-Welfare-Management-System\hms\templates\hms\admin\visitor_management.html',
    r'c:\Users\jamal\Downloads\Student-Welfare-Management-System\Student-Welfare-Management-System\hms\templates\hms\admin\dashboard.html',
    r'c:\Users\jamal\Downloads\Student-Welfare-Management-System\Student-Welfare-Management-System\hms\templates\hms\admin\analytics_dashboard.html',
]

# Common patterns to fix across all templates
common_fixes = [
    # Student names
    (r'{{\s*\r?\n\s*deferment\.student\.user\.get_full_name\s*}}', '{{ deferment.student.user.get_full_name }}'),
    (r'{{\s*\r?\n\s*leave\.student\.user\.get_full_name\s*}}', '{{ leave.student.user.get_full_name }}'),
    (r'{{\s*\r?\n\s*l\.student\.user\.get_full_name\s*}}', '{{ l.student.user.get_full_name }}'),
    (r'{{\s*\r?\n\s*student\.user\.get_full_name\s*}}', '{{ student.user.get_full_name }}'),
    
    # University IDs
    (r'{{\s*deferment\.student\.university_id\s*\r?\n\s*}}', '{{ deferment.student.university_id }}'),
    (r'{{\s*leave\.student\.university_id\s*\r?\n\s*}}', '{{ leave.student.university_id }}'),
    
    # Phone numbers
    (r'{{\s*deferment\.student\.phone\|default:"Not\s*\r?\n\s*provided"\s*}}', '{{ deferment.student.phone|default:"Not provided" }}'),
    (r'{{\s*leave\.student\.phone\|default:"Not\s*\r?\n\s*provided"\s*}}', '{{ leave.student.phone|default:"Not provided" }}'),
    
    # Room numbers
    (r'{{\s*\r?\n\s*deferment\.student\.room_number\|default:"Not assigned"\s*}}', '{{ deferment.student.room_number|default:"Not assigned" }}'),
    (r'{{\s*\r?\n\s*leave\.student\.room_number\|default:"Not assigned"\s*}}', '{{ leave.student.room_number|default:"Not assigned" }}'),
    
    # Dates
    (r'{{\s*\r?\n\s*deferment\.end_date\|date:"M d, Y"\s*}}', '{{ deferment.end_date|date:"M d, Y" }}'),
    (r'{{\s*\r?\n\s*leave\.end_date\|date:"M d, Y"\s*}}', '{{ leave.end_date|date:"M d, Y" }}'),
    (r'{{\s*\r?\n\s*l\.end_date\|date:"M d, Y"\s*}}', '{{ l.end_date|date:"M d, Y" }}'),
    
    # Leave types
    (r'{{\s*\r?\n\s*leave\.get_leave_type_display\s*}}', '{{ leave.get_leave_type_display }}'),
    (r'{{\s*\r?\n\s*l\.get_leave_type_display\s*}}', '{{ l.get_leave_type_display }}'),
    
    # Visitor records
    (r'{{\s*\r?\n\s*active_visitors\.count\s*}}', '{{ active_visitors.count }}'),
    (r'{{\s*\r?\n\s*visitor\.student\.user\.get_full_name\s*}}', '{{ visitor.student.user.get_full_name }}'),
    (r'{{\s*\r?\n\s*visitor\.student\.room_number\s*}}', '{{ visitor.student.room_number }}'),
    
    # Dashboard meal records
    (r'{{\s*\r?\n\s*records\|length\s*}}', '{{ records|length }}'),
    (r'{{\s*\r?\n\s*away_students\|length\s*}}', '{{ away_students|length }}'),
    
    # Any remaining generic splits
    (r'{{\s*\r?\n\s*([a-zA-Z0-9_\.|\'":\s]+)\s*}}', r'{{ \1 }}'),
]

fixed_count = 0
for file_path in files_to_fix:
    if not os.path.exists(file_path):
        print(f"⚠️  Skipping {os.path.basename(file_path)} - file not found")
        continue
        
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    content = original_content
    
    # Apply all fixes
    for pattern, replacement in common_fixes:
        content = re.sub(pattern, replacement, content)
    
    # Only write if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed {os.path.basename(file_path)}")
        fixed_count += 1
    else:
        print(f"✓  No changes needed in {os.path.basename(file_path)}")

print(f"\n🎉 Successfully fixed {fixed_count} template file(s)!")
