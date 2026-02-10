
import os

view_path = r'hms\views.py'

mappings = {
    "@role_required(['Admin', 'Warden', 'Finance'])": "@role_required(['Admin', 'Warden', 'Finance', 'DEFERMENT', 'MAINTENANCE_HOSTEL', 'ACTIVITIES_ROOMS', 'NEWS_ALERT', 'VISITORS', 'AUDIT_LOGS'])",
    "@role_required(['Admin', 'Warden'])": "@role_required(['Admin', 'Warden', 'Finance', 'DEFERMENT', 'MAINTENANCE_HOSTEL', 'ACTIVITIES_ROOMS', 'NEWS_ALERT', 'VISITORS', 'AUDIT_LOGS'])",
    "@role_required(['Admin', 'Finance'])": "@role_required(['Admin', 'Finance', 'MAINTENANCE_HOSTEL'])",
    "@role_required(['Admin', 'Warden'])": "@role_required(['Admin', 'Warden', 'DEFERMENT'])", # This might clash with the one above, I'll be careful
}

# Specific mapping for dashboard_admin (line 477 approx)
# Specific mapping for export_meals_csv (line 669 approx)
# Specific mapping for export_students_csv (line 703 approx)

with open(view_path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    replaced = False
    # Handle dashboard_admin, export_meals_csv, export_students_csv which use ['Admin', 'Warden', 'Finance'] or ['Admin', 'Warden']
    if "@role_required(['Admin', 'Warden', 'Finance'])" in line:
        new_lines.append(line.replace("@role_required(['Admin', 'Warden', 'Finance'])", "@role_required(['Admin', 'Warden', 'Finance', 'DEFERMENT', 'MAINTENANCE_HOSTEL', 'ACTIVITIES_ROOMS', 'NEWS_ALERT', 'VISITORS', 'AUDIT_LOGS'])"))
        replaced = True
    elif "@role_required(['Admin', 'Warden'])" in line:
        # Check if it's deferment-related or general export
        # If it's near line 669 or 703, it's general
        # If it's near line 1830, it's deferment
        # I'll just use a smarter check
        pass # Handle below
    
    if not replaced:
        new_lines.append(line)

# Let's try a more robust approach by specific line numbers or better context
with open(view_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Primary targets
content = content.replace("@role_required(['Admin', 'Warden', 'Finance'])", "@role_required(['Admin', 'Warden', 'Finance', 'DEFERMENT', 'MAINTENANCE_HOSTEL', 'ACTIVITIES_ROOMS', 'NEWS_ALERT', 'VISITORS', 'AUDIT_LOGS'])")

# Payment
content = content.replace("@role_required(['Admin', 'Finance'])", "@role_required(['Admin', 'Finance', 'MAINTENANCE_HOSTEL'])")

# These need context or multiple replaces
# I'll replace the ones I know are general first
content = content.replace("def export_meals_csv(request):", "def_export_meals_csv_placeholder")
content = content.replace("def export_students_csv(request):", "def_export_students_csv_placeholder")

# Now I change the ones for exports
# Actually, I'll just change ALL [@role_required(['Admin', 'Warden'])] to the broad one if they are for exports
# And then handle deferment specifically

# I'll just do it simply:
import re
# dashboard_admin (already handled if it was exact match, but let's be sure)
content = re.sub(r"@role_required\(\['Admin', 'Warden', 'Finance'\]\)", "@role_required(['Admin', 'Warden', 'Finance', 'DEFERMENT', 'MAINTENANCE_HOSTEL', 'ACTIVITIES_ROOMS', 'NEWS_ALERT', 'VISITORS', 'AUDIT_LOGS'])", content)

# General exports (Admin, Warden) -> Broad
# We'll use the function name as anchor
content = re.sub(r"@role_required\(\['Admin', 'Warden'\]\)\ndef export_meals_csv", "@role_required(['Admin', 'Warden', 'Finance', 'DEFERMENT', 'MAINTENANCE_HOSTEL', 'ACTIVITIES_ROOMS', 'NEWS_ALERT', 'VISITORS', 'AUDIT_LOGS'])\ndef export_meals_csv", content)
content = re.sub(r"@role_required\(\['Admin', 'Warden'\]\)\ndef export_students_csv", "@role_required(['Admin', 'Warden', 'Finance', 'DEFERMENT', 'MAINTENANCE_HOSTEL', 'ACTIVITIES_ROOMS', 'NEWS_ALERT', 'VISITORS', 'AUDIT_LOGS'])\ndef export_students_csv", content)

# Maintenance
content = re.sub(r"@role_required\(\['Admin', 'Warden'\]\)\ndef manage_maintenance", "@role_required(['Admin', 'Warden', 'MAINTENANCE_HOSTEL', 'ACTIVITIES_ROOMS'])\ndef manage_maintenance", content)
content = re.sub(r"@role_required\(\['Admin', 'Warden'\]\)\ndef update_maintenance_status", "@role_required(['Admin', 'Warden', 'MAINTENANCE_HOSTEL', 'ACTIVITIES_ROOMS'])\ndef update_maintenance_status", content)

# Deferment
content = re.sub(r"@role_required\(\['Admin', 'Warden'\]\)\ndef admin_deferment_all", "@role_required(['Admin', 'Warden', 'DEFERMENT'])\ndef admin_deferment_all", content)
content = re.sub(r"@role_required\(\['Admin', 'Warden'\]\)\ndef review_deferment", "@role_required(['Admin', 'Warden', 'DEFERMENT'])\ndef review_deferment", content)

with open(view_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patching complete.")
