from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test_login(request):
    """Temporary test login view without CSRF protection"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            
            if user.is_staff:
                return redirect('hms:admin_dashboard')
            return redirect('hms:student_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'hms/login.html', {'form': form})
