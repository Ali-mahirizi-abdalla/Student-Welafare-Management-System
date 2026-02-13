from django.template import loader, TemplateSyntaxError
import sys

try:
    loader.get_template('hms/admin/dashboard.html')
    print('SUCCESS')
except TemplateSyntaxError as e:
    print(f'SYNTAX_ERROR: {e}')
    # Extract line number if possible
    # We can try to get more details from the exception
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f'ERROR: {type(e).__name__}: {e}')
