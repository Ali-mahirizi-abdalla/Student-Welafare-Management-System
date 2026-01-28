
path = r"c:\Users\jamal\Downloads\Student-Welfare-Management-System\Student-Welfare-Management-System\Student_Welfare_System\management\__init__.py"
try:
    with open(path, 'rb') as f:
        print(f"Content: {f.read()}")
except Exception as e:
    print(f"Error: {e}")
