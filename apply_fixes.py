import os

def apply_fixes():
    print("Applying fixes...")
    
    # helper
    def load(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def save(path, content):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {path}")

    # 1. edit_student.html
    path1 = r"hms/templates/hms/admin/edit_student.html"
    if os.path.exists(path1):
        c = load(path1)
        # simplistic replacements for this specific file
        c = c.replace('{% if student.county==code %}', '{% if student.county == code %}')
        c = c.replace('{% if student.gender==code %}', '{% if student.gender == code %}')
        c = c.replace('{% if student.disability==code %}', '{% if student.disability == code %}')
        c = c.replace('{% if\n                                    student.residence_type==code %}', '{% if\n                                    student.residence_type == code %}')
        # Also try single line version just in case normalization happened
        c = c.replace('{% if student.residence_type==code %}', '{% if student.residence_type == code %}') 
        c = c.replace('{% if student.hostel==code %}', '{% if student.hostel == code %}')
        save(path1, c)
    else:
        print(f"Skipped {path1} (not found)")

    # 2. manage_payments.html
    path2 = r"hms/templates/hms/admin/manage_payments.html"
    if os.path.exists(path2):
        c = load(path2)
        c = c.replace("status_filter=='Completed'", "status_filter == 'Completed'")
        c = c.replace("status_filter=='Pending'", "status_filter == 'Pending'")
        c = c.replace("status_filter=='Failed'", "status_filter == 'Failed'")
        save(path2, c)
    else:
        print(f"Skipped {path2} (not found)")

    # 3. event_detail.html
    path3 = r"hms/templates/hms/events/event_detail.html"
    if os.path.exists(path3):
        c = load(path3)
        c = c.replace("event.spots_remaining> 0", "event.spots_remaining > 0")
        save(path3, c)
    else:
        print(f"Skipped {path3} (not found)")

    # 4. event_attendees.html
    path4 = r"hms/templates/hms/events/event_attendees.html"
    if os.path.exists(path4):
        c = load(path4)
        # This one is tricky: multiline split if.
        # Original:
        # <span class="...">{ % if
        #     rsvp.attended %}Present{% else %}Absent{% endif %}</span>
        
        # We want to join it or just make it standard.
        # Let's try to match the specific split string if possible.
        old_str = '{% if\n                                        rsvp.attended %}Present{% else %}Absent{% endif %}'
        new_str = '{% if rsvp.attended %}Present{% else %}Absent{% endif %}'
        
        # Since indentation might vary, let's use a regex or just read the file and look for it.
        # Actually simplest is just to replace the distinct parts if they are unique enough.
        # But 'rsvp.attended' might appear elsewhere? No.
        
        import re
        pattern = r'\{\%\s*if\s*\n\s*rsvp\.attended\s*\%\}\s*Present\s*\{\%\s*else\s*\%\}\s*Absent\s*\{\%\s*endif\s*\%\}'
        
        # Check if we can find it
        match = re.search(pattern, c)
        if match:
             print("Found broken tag in event_attendees.html")
             c = re.sub(pattern, '{% if rsvp.attended %}Present{% else %}Absent{% endif %}', c)
        else:
             print("Could not find broken tag pattern in event_attendees.html, trying simple join")
             # Fallback: maybe it's not exactly as expected?
             # Let's try to find line 120/121 location.
             pass

        # Also fix the {{ empty }} -> {% empty %}
        c = c.replace('{{ empty }}', '{% empty %}')
        
        save(path4, c)
    else:
        print(f"Skipped {path4} (not found)")

if __name__ == "__main__":
    apply_fixes()
