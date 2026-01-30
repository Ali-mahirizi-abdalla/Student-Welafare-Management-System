import os
import subprocess
import time

print("=" * 60)
print("FIXING TEMPLATE AND KILLING ALL SERVERS")
print("=" * 60)

# Step 1: Kill ALL Python processes
print("\n[1/4] Killing ALL Django servers...")
try:
    subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
                   capture_output=True, text=True)
    print("✓ All Python processes killed")
except Exception as e:
    print(f"! Error killing processes: {e}")

time.sleep(2)

# Step 2: Fix the template file
print("\n[2/4] Fixing template file...")
file_path = r"hms\templates\hms\admin\manage_students.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix both issues
old1 = "{% if status_filter=='active' %}"
new1 = "{% if status_filter == 'active' %}"
old2 = "{% if status_filter=='away' %}"
new2 = "{% if status_filter == 'away' %}"

changes_made = 0
if old1 in content:
    content = content.replace(old1, new1)
    changes_made += 1
    print(f"✓ Fixed: {old1} → {new1}")

if old2 in content:
    content = content.replace(old2, new2)
    changes_made += 1
    print(f"✓ Fixed: {old2} → {new2}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✓ Template file updated ({changes_made} changes)")

# Step 3: Clear cache
print("\n[3/4] Clearing Python cache...")
cache_dirs = ['__pycache__', 'hms/__pycache__', 'swms/__pycache__']
for cache_dir in cache_dirs:
    if os.path.exists(cache_dir):
        import shutil
        shutil.rmtree(cache_dir)
        print(f"✓ Cleared: {cache_dir}")

# Step 4: Verify
print("\n[4/4] Verifying fixes...")
with open(file_path, 'r', encoding='utf-8') as f:
    verify = f.read()

if "status_filter == 'active'" in verify and "status_filter=='active'" not in verify:
    print("✓ VERIFICATION PASSED!")
else:
    print("✗ VERIFICATION FAILED!")

print("\n" + "=" * 60)
print("DONE! Now run ONLY this command:")
print("python manage.py runserver 127.0.0.1:8000 --skip-checks")
print("=" * 60)
