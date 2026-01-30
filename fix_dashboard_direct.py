#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Direct fix for dashboard.html split variables"""

file_path = r'c:\Users\jamal\Downloads\Student-Welfare-Management-System\Student-Welfare-Management-System\hms\templates\hms\admin\dashboard.html'

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines before: {len(lines)}")

# Find and fix line by line
i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if this line ends with {{ and next line has the closing }}
    if '{{' in line and not '}}' in line and i + 1 < len(lines):
        next_line = lines[i + 1]
        if '}}' in next_line:
            # Merge the lines
            merged = line.rstrip('\r\n') + ' ' + next_line.lstrip()
            lines[i] = merged
            del lines[i + 1]
            print(f"Fixed split at line {i+1}: {merged.strip()[:80]}...")
            continue
    
    i += 1

print(f"Total lines after: {len(lines)}")

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Dashboard.html fixed!")
