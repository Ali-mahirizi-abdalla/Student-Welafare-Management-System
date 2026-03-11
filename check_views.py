import py_compile
import traceback

try:
    py_compile.compile('hms/views.py', doraise=True)
except Exception as e:
    with open('err.txt', 'w', encoding='utf-8') as f:
        f.write(traceback.format_exc())
