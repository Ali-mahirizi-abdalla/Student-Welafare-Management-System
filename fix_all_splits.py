#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Comprehensive fix for ALL split template variables"""

import re
import os
import glob

# Get all HTML files in admin templates
template_dir = r'c:\Users\jamal\Downloads\Student-Welfare-Management-System\Student-Welfare-Management-System\hms\templates\hms\admin'
html_files = glob.glob(os.path.join(template_dir, '*.html'))

def fix_template_file(file_path):
    """Fix split template variables in a single file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Strategy 1: Fix any {{ that appears at end of line (most comprehensive)
    # This catches ANY split variable regardless of what's inside
    content = re.sub(r'{{\s*([^}]+?)\s*\r?\n\s+([^}]+?)\s*}}', r'{{ \1 \2 }}', content)
    
    # Strategy 2: Clean up any remaining multi-line splits with more than 2 lines
    # Keep applying until no more matches
    max_iterations = 5
    for _ in range(max_iterations):
        old_content = content
        content = re.sub(r'{{\s*([^}]+?)\s*\r?\n\s+([^}]+?)\s*\r?\n\s+([^}]+?)\s*}}', r'{{ \1 \2 \3 }}', content)
        if content == old_content:
            break
    
    # Strategy 3: Clean up any excessive whitespace within template tags
    content = re.sub(r'{{\s+([^}]+?)\s+}}', r'{{ \1 }}', content)
    
    # Strategy 4: Fix specific known patterns that might remain
    specific_fixes = [
        # Meal student names
        (r'{{\s*meal\.student\.user\.get_full_name\s*\r?\n[^}]*}}', '{{ meal.student.user.get_full_name }}'),
        # Chart data
        (r'{{\s*chart_data_json\|\s*safe\s*\r?\n[^}]*}}', '{{ chart_data_json|safe }}'),
        # Visitor room numbers with default
        (r'{{\s*visitor\.student\.room_number\|default:"No\s*\r?\n\s*room"\s*}}', '{{ visitor.student.room_number|default:"No room" }}'),
        # Date formats
        (r'{{\s*visitor\.check_in_time\|date:"M d, H:i"\s*\r?\n[^}]*}}', '{{ visitor.check_in_time|date:"M d, H:i" }}'),
        (r'{{\s*leave_request\.start_date\|date:"M d, Y"\s*\r?\n[^}]*}}', '{{ leave_request.start_date|date:"M d, Y" }}'),
        # Activity dates
        (r'{{\s*activity\.date\|date:"M j"\s*}}\s*•\s*{{\s*\r?\n[^}]*}}', '{{ activity.date|date:"M j" }} • {{ activity.time }}'),
    ]
    
    for pattern, replacement in specific_fixes:
        content = re.sub(pattern, replacement, content)
    
    # Return whether changes were made and the new content
    return content != original_content, content

print("=" * 60)
print("COMPREHENSIVE TEMPLATE VARIABLE FIX")
print("=" * 60)

fixed_count = 0
for file_path in html_files:
    file_name = os.path.basename(file_path)
    
    try:
        changed, new_content = fix_template_file(file_path)
        
        if changed:
            # Write the fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Fixed: {file_name}")
            fixed_count += 1
        else:
            print(f"✓  OK: {file_name}")
    except Exception as e:
        print(f"❌ Error fixing {file_name}: {e}")

print("=" * 60)
print(f"🎉 Successfully fixed {fixed_count} file(s)!")
print("=" * 60)
