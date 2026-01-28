
import os

files = [
    r"c:\Users\jamal\Downloads\Student-Welfare-Management-System\Student-Welfare-Management-System\Student_Welfare_System\management\__init__.py",
    r"c:\Users\jamal\Downloads\Student-Welfare-Management-System\Student-Welfare-Management-System\Student_Welfare_System\management\commands\__init__.py"
]

for path in files:
    print(f"fixing {path}")
    with open(path, 'w', encoding='utf-8') as f:
        f.write("")
    print("Done.")
