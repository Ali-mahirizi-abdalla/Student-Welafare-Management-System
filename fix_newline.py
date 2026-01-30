import os
import re

print("Searching for manage_students.html...")
found_files = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file == "manage_students.html":
            found_files.append(os.path.join(root, file))

print(f"Found {len(found_files)} files: {found_files}")

for file_path in found_files:
    print(f"\nProcessing: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find the broken tag with newline
    pattern = r"\{\{\s*student\.user\.get_full_name\s*\n\s+\}\}"
    match = re.search(pattern, content)
    
    if match:
        print("✓ Found broken tag pattern!")
        # Replace matches
        new_content = re.sub(pattern, "{{ student.user.get_full_name }}", content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✓ Fixed broken tag!")
    else:
        print("✗ Broken tag not found (might be already fixed or different format)")
        # Check if correct tag exists
        if "{{ student.user.get_full_name }}" in content:
            print("  - Correct tag alrady present.")

    # Verify
    with open(file_path, 'r', encoding='utf-8') as f:
        verify = f.read()
    
    if "{{ student.user.get_full_name }}" in verify:
         print("  -> Verification: Tag looks correct now.")
    else:
         print("  -> Verification FAILED: Tag incorrectly formatted.")
