import os

file_path = r"hms\templates\hms\admin\manage_students.html"

print(f"Reading file: {file_path}")

# Read the current content
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the problematic lines
print("Making replacements...")
old_pattern1 = "{% if status_filter=='active' %}"
new_pattern1 = "{% if status_filter == 'active' %}"

old_pattern2 = "{% if status_filter=='away' %}"
new_pattern2 = "{% if status_filter == 'away' %}"

if old_pattern1 in content:
    print(f"Found: {old_pattern1}")
    content = content.replace(old_pattern1, new_pattern1)
    print(f"Replaced with: {new_pattern1}")
else:
    print(f"NOT FOUND: {old_pattern1}")

if old_pattern2 in content:
    print(f"Found: {old_pattern2}")
    content = content.replace(old_pattern2, new_pattern2)
    print(f"Replaced with: {new_pattern2}")
else:
    print(f"NOT FOUND: {old_pattern2}")

# Write the content back
print("\nWriting file...")
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("File written successfully!")

# Verify the change
print("\nVerifying changes...")
with open(file_path, 'r', encoding='utf-8') as f:
    verify_content = f.read()
    
if "status_filter == 'active'" in verify_content:
    print("✓ Verification PASSED: Fixed syntax found in file")
else:
    print("✗ Verification FAILED: Old syntax still present")

if "status_filter=='active'" in verify_content:
    print("✗ WARNING: Old syntax still found in file!")
else:
    print("✓ Old syntax removed successfully")
