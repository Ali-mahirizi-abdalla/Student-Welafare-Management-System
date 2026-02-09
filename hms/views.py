from django.shortcuts import render, redirect, get_object_or_404
# Trigger reload
from django.conf import settings
from django.core.paginator import Paginator
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import (Student, Meal, Activity, AwayPeriod, Announcement, Document, MaintenanceRequest,
                     Message, AuditLog,
                     LeaveRequest, DefermentRequest, Visitor,
                     Room, RoomAssignment, RoomChangeRequest, Payment, Notification, LoginActivity, LostItem)
from .decorators import role_required, admin_only

# ==================== Authentication ====================
from .forms import (
    StudentRegistrationForm, ProfileEditForm, AwayModeForm, ActivityForm, DocumentForm, 
    TimetableForm, RoomSelectionForm, MessageForm, MaintenanceRequestForm,
    MaintenanceStatusForm, RoomForm, RoomAssignmentForm, RoomChangeRequestForm,
    LeaveRequestForm, DefermentRequestForm, LeaveApprovalForm, VisitorForm, AnnouncementForm, LostItemForm
)
from datetime import date, datetime, time, timedelta
from django.db import transaction, models
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import json
from .mpesa import MpesaClient

# ==================== Authentication ====================

def register_student(request):
    """
    Handle student registration logic.
    Creates a user and a student profile within a transaction.
    """
    if request.method == 'POST':
        print("DEBUG: Registration POST received")
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            print("DEBUG: Form is valid")
            try:
                with transaction.atomic():
                    student = form.save()
                    print(f"DEBUG: Student created: {student}")
                
                # Log in AFTER transaction commits
                login(request, student.user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, 'Registration successful!')
                return redirect('hms:student_dashboard')

            except Exception as e:
                print(f"DEBUG: Registration Exception: {e}")
                import traceback
                traceback.print_exc()
                messages.error(request, f"Registration failed: {str(e)}")
        else:
            print(f"DEBUG: Form Errors: {form.errors}")
            for field, errors in form.errors.items():
                messages.error(request, f"{field}: {', '.join(errors)}")
    else:
        form = StudentRegistrationForm()
    return render(request, 'hms/register.html', {'form': form})


def user_login(request):
    """Login view for all users with role selection"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('hms:admin_dashboard')
        return redirect('hms:student_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            
            # Get selected role from dropdown
            selected_role = request.POST.get('role', 'student')
            
            # Redirect based on selected role (with permission check)
            if selected_role == 'admin':
                if user.is_staff:
                    return redirect('hms:admin_dashboard')
                else:
                    messages.warning(request, 'You do not have admin privileges. Redirecting to student dashboard.')
                    return redirect('hms:student_dashboard')
            else:
                return redirect('hms:student_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'hms/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('hms:login')

def terms_and_conditions(request):
    """Terms and Conditions page"""
    return render(request, 'hms/terms.html')

@login_required
def global_search(request):
    """Global search across students, announcements, and maintenance requests"""
    query = request.GET.get('q', '').strip()
    
    context = {
        'query': query,
        'students': [],
        'announcements': [],
        'maintenance': [],
        'total_count': 0,
    }
    
    if query:
        # Search students (admin only)
        if request.user.is_staff:
            students = Student.objects.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(university_id__icontains=query) |
                Q(phone__icontains=query)
            ).select_related('user')[:10]
            context['students'] = students
        
        # Search announcements
        announcements = Announcement.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query),
            is_active=True
        ).order_by('-created_at')[:10]
        context['announcements'] = announcements
        
        # Search maintenance requests (own requests for students, all for admin)
        if request.user.is_staff:
            maintenance = MaintenanceRequest.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query)
            ).select_related('student__user').order_by('-created_at')[:10]
        else:
            try:
                student = request.user.student_profile
                maintenance = MaintenanceRequest.objects.filter(
                    student=student
                ).filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(location__icontains=query)
                ).order_by('-created_at')[:10]
            except Student.DoesNotExist:
                maintenance = []
        
        context['maintenance'] = maintenance
        context['total_count'] = len(context['students']) + len(context['announcements']) + len(context['maintenance'])
    
    return render(request, 'hms/search_results.html', context)


# ==================== Student ====================

@login_required
def student_dashboard(request):
    """
    Main dashboard for students.
    Displays:
    - Meal status for today/tomorrow
    - Daily announcements
    - Activities
    - Quick actions (Away mode, etc.)
    """
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        if request.user.is_staff:
            return redirect('hms:admin_dashboard')
        # Auto-create profile
        student = Student.objects.create(user=request.user, university_id=None)
        messages.warning(request, "Profile was missing and has been created.")
        
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    # Check if currently away
    is_away_today = AwayPeriod.objects.filter(student=student, start_date__lte=today, end_date__gte=today).exists()
    is_away_tomorrow = AwayPeriod.objects.filter(student=student, start_date__lte=tomorrow, end_date__gte=tomorrow).exists()

    # Get meal status for today and tomorrow
    meal_today, _ = Meal.objects.get_or_create(student=student, date=today)
    if is_away_today and not meal_today.away:
         # Auto-correct to away if valid period exists
         meal_today.away = True
         meal_today.breakfast = False
         meal_today.early = False
         meal_today.supper = False
         meal_today.save()

    meal_tomorrow, _ = Meal.objects.get_or_create(student=student, date=tomorrow)
    if is_away_tomorrow and not meal_tomorrow.away:
         meal_tomorrow.away = True
         meal_tomorrow.breakfast = False
         meal_tomorrow.early = False
         meal_tomorrow.supper = False
         meal_tomorrow.save()
    
    # Check lock time for UI display
    now = timezone.now()
    lock_time = time(8, 0)
    is_locked = (now.time() > lock_time)

    # Away Mode Form
    away_form = AwayModeForm()

    context = {
        'student': student,
        'meal_today': meal_today,
        'meal_tomorrow': meal_tomorrow,
        'is_locked': is_locked,
        'today': today,
        'tomorrow': tomorrow,
        'is_away_today': is_away_today,
        'is_away_tomorrow': is_away_tomorrow,
        'away_form': away_form,
        # Pre-calculated attributes for template to avoid formatter breaking split tags
        'today_breakfast_attr': 'checked' if meal_today.breakfast else '',
        'today_early_attr': 'checked' if meal_today.early else '',
        'today_supper_attr': 'checked' if meal_today.supper else '',
        'today_disabled_attr': 'disabled' if (is_locked or is_away_today) else '',
        'tomorrow_breakfast_attr': 'checked' if meal_tomorrow.breakfast else '',
        'tomorrow_early_attr': 'checked' if meal_tomorrow.early else '',
        'tomorrow_supper_attr': 'checked' if meal_tomorrow.supper else '',
        'tomorrow_disabled_attr': 'disabled' if is_away_tomorrow else '',
        'announcements': Announcement.objects.filter(is_active=True).order_by('-created_at')[:5],
        'activities': Activity.objects.filter(active=True).order_by('weekday', 'time'),
        'documents': Document.objects.all().order_by('-uploaded_at'),
        'unread_messages': Message.objects.filter(recipient=request.user, is_read=False).count(),
    }
    return render(request, 'hms/student/dashboard.html', context)

@login_required
def student_profile(request):
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        student = Student.objects.create(user=request.user, university_id=None)
        messages.warning(request, "Profile was missing and has been created.")

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = ProfileEditForm(
                request.POST,
                user=request.user,
                student=student
            )
            
            if profile_form.is_valid():
                # Handle profile image separately
                if 'profile_image' in request.FILES:
                    student.profile_image = request.FILES['profile_image']
                    student.save()
                
                # Save form data (user and student fields)
                profile_form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('hms:student_profile')
            else:
                for field, errors in profile_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
    else:
        profile_form = ProfileEditForm(user=request.user, student=student)

    # Get recent meal history (Only today and future, as history disappears after 24h)
    meal_history = student.meals.filter(date__gte=date.today()).order_by('date')[:10]
    
    # Forms
    room_form = RoomSelectionForm(instance=student)
    timetable_form = TimetableForm(instance=student)

    context = {
        'student': student,
        'meal_history': meal_history,
        'room_form': room_form,
        'timetable_form': timetable_form,
        'profile_form': profile_form,
    }
    return render(request, 'hms/student/profile.html', context)


@login_required
def confirm_meals(request):
    """Handle meal confirmation"""
    if request.method != 'POST':
        return HttpResponseForbidden("Method not allowed")
    
    try:
        student = request.user.student_profile
        meal_date_str = request.POST.get('date')
        meal_date = datetime.strptime(meal_date_str, '%Y-%m-%d').date()

        # Check away status first
        if AwayPeriod.objects.filter(student=student, start_date__lte=meal_date, end_date__gte=meal_date).exists():
            messages.error(request, "You are marked as away for this date. Change your 'Away Mode' settings first.")
            return redirect('hms:student_dashboard')
        
        # Enforce 8:00 AM Lock for breakfast/early
        now = timezone.now()
        current_time = now.time()
        lock_time = time(8, 0)
        is_today = (meal_date == date.today())
        
        breakfast = request.POST.get('breakfast') == 'on'
        early = request.POST.get('early') == 'on'
        supper = request.POST.get('supper') == 'on'
        
        if is_today and current_time > lock_time:
            # Cannot change breakfast/early settings after lock time
            existing, _ = Meal.objects.get_or_create(student=student, date=meal_date)
            breakfast = existing.breakfast
            early = existing.early 
            messages.warning(request, "Breakfast options are locked for today after 08:00 AM.")
            
        Meal.objects.update_or_create(
            student=student,
            date=meal_date,
            defaults={
                'breakfast': breakfast,
                'early': early,
                'supper': supper,
                'away': False
            }
        )
        messages.success(request, f"Meals updated for {meal_date}")
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        
    return redirect('hms:student_dashboard')

@login_required
def toggle_away_mode(request):
    if request.method == 'POST':
        form = AwayModeForm(request.POST)
        if form.is_valid():
            try:
                student = request.user.student_profile
                away_period = form.save(commit=False)
                away_period.student = student
                away_period.save()
                
                # Auto-update meals in this range to Away=True, Others=False
                cur_date = away_period.start_date
                while cur_date <= away_period.end_date:
                    Meal.objects.update_or_create(
                        student=student,
                        date=cur_date,
                        defaults={'away': True, 'breakfast': False, 'early': False, 'supper': False}
                    )
                    cur_date += timedelta(days=1)
                    
                messages.success(request, f"Away mode set from {away_period.start_date} to {away_period.end_date}")
            except Exception as e:
                 messages.error(request, f"Error setting away mode: {str(e)}")
        else:
            messages.error(request, "Invalid dates provided.")
    return redirect('hms:student_dashboard')

@login_required
def toggle_early_breakfast(request):
    return redirect('hms:student_dashboard')

# ==================== Admin/Kitchen ====================

@login_required
@role_required(['Admin', 'Warden', 'Finance'])
def dashboard_admin(request):
    """Kitchen/Admin Dashboard"""
    # Auto-redirect for student attempting to access admin url handled by decorator (or 403)

    
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    # Counts for Today
    today_stats = {
        'breakfast': Meal.objects.filter(date=today, breakfast=True).count(),
        'early': Meal.objects.filter(date=today, early=True).count(),
        'supper': Meal.objects.filter(date=today, supper=True).count(),
        'away': Meal.objects.filter(date=today, away=True).count(),
    }
    
    # Counts for Tomorrow
    tomorrow_stats = {
        'breakfast': Meal.objects.filter(date=tomorrow, breakfast=True).count(),
        'early': Meal.objects.filter(date=tomorrow, early=True).count(),
        'supper': Meal.objects.filter(date=tomorrow, supper=True).count(),
    }
    
    total_students = Student.objects.count()
    
    # Deferment count (pending leave requests)
    deferment_count = LeaveRequest.objects.filter(status='pending').count()
    
    # Residence type counts
    off_campus_count = Student.objects.filter(residence_type='off_campus').count()
    in_hostel_count = Student.objects.filter(residence_type='hostel').count()
    
    # Bed capacity and room statistics
    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(is_available=False).count()
    total_bed_capacity = Room.objects.filter(is_available=True).aggregate(total=models.Sum('capacity'))['total'] or 0
    
    # Meal plan status (students who have submitted meal choices for today)
    student_on_meals = Meal.objects.filter(date=today).values('student').distinct().count()
    
    # Menu items count (active activities for today)
    activities = Activity.objects.filter(active=True)
    today_activity = activities.filter(weekday=today.weekday()).first()
    menu_count = 1 if today_activity else 0 # Simple count for now, could be expanded
    
    # Real counts from database
    attachment_count = Student.objects.filter(is_on_attachment=True).count()
    graduating_count = Student.objects.filter(is_graduating=True).count()
    
    context = {
        'today': today,
        'tomorrow': tomorrow,
        'today_stats': today_stats,
        'tomorrow_stats': tomorrow_stats,
        'total_students': total_students,
        'deferment_count': deferment_count,
        'off_campus_count': off_campus_count,
        'in_hostel_count': in_hostel_count,
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'total_bed_capacity': total_bed_capacity,
        'student_on_meals': student_on_meals,
        'menu_count': menu_count,
        'attachment_count': attachment_count,
        'graduating_count': graduating_count,
        'today_activity': today_activity,
        'activities': activities
    }

    # ==================== ADVANCED DASHBOARD LOGIC ====================
    
    # 1. Search & Filtering
    search_query = request.GET.get('q', '')
    filter_date_str = request.GET.get('date', str(today))
    
    try:
        filter_date = datetime.strptime(filter_date_str, '%Y-%m-%d').date()
    except ValueError:
        filter_date = today

    # Base Queryset for Today's Meals (or filtered date)
    meals_query = Meal.objects.filter(date=filter_date).select_related('student__user')
    
    if search_query:
        meals_query = meals_query.filter(
            models.Q(student__user__first_name__icontains=search_query) | 
            models.Q(student__user__last_name__icontains=search_query) |
            models.Q(student__university_id__icontains=search_query)
        )

    # 2. Daily Lists
    present_list = meals_query.filter(away=False)
    
    # Filter by meal type if requested
    filter_type = request.GET.get('filter')
    if filter_type == 'breakfast':
        present_list = present_list.filter(breakfast=True)
    elif filter_type == 'supper':
        present_list = present_list.filter(supper=True)
    elif filter_type == 'early':
        present_list = present_list.filter(early=True)

    # Students who have explicitly set 'away' to True for this date
    away_list_consult = meals_query.filter(away=True)
    
    # 3. Notifications / "Unconfirmed" 
    # Logic: Students who have a profile but NO meal record for tomorrow
    # This might differ based on business logic, here assuming "No Record" = Unconfirmed
    all_student_ids = Student.objects.values_list('id', flat=True)
    confirmed_student_ids_tomorrow = Meal.objects.filter(date=tomorrow).values_list('student_id', flat=True)
    unconfirmed_count = len(all_student_ids) - len(confirmed_student_ids_tomorrow)

    # 4. Chart Data: Weekly Trends (Last 7 Days)
    week_start = today - timedelta(days=6)
    weekly_labels = []
    weekly_registrations = []
    weekly_payments = []
    weekly_maintenance = []
    weekly_visitors = []
    weekly_meals = []
    
    for i in range(7):
        d = week_start + timedelta(days=i)
        weekly_labels.append(d.strftime('%a')) # Mon, Tue...
        
        # Registrations count for this day
        reg_count = Student.objects.filter(created_at__date=d).count()
        weekly_registrations.append(reg_count)
        
        # Payments count for this day
        pay_count = Payment.objects.filter(created_at__date=d, status='Completed').count()
        weekly_payments.append(pay_count)

        # Maintenance requests count for this day
        maint_count = MaintenanceRequest.objects.filter(created_at__date=d).count()
        weekly_maintenance.append(maint_count)

        # Visitor Logs count for this day
        visit_count = Visitor.objects.filter(check_in_time__date=d).count()
        weekly_visitors.append(visit_count)
        
        # Total meals Activity (Breakfast OR Supper)
        meal_activity = Meal.objects.filter(date=d).filter(models.Q(breakfast=True) | models.Q(supper=True)).count()
        weekly_meals.append(meal_activity)

    import json
    chart_data = {
        'weekly_labels': weekly_labels,
        'weekly_registrations': weekly_registrations,
        'weekly_payments': weekly_payments,
        'weekly_maintenance': weekly_maintenance,
        'weekly_visitors': weekly_visitors,
        'weekly_meals': weekly_meals,
    }

    # 5. Recent Activity (Audit Logs)
    from .models import AuditLog
    recent_activity = AuditLog.objects.all().select_related('user__student_profile').order_by('-timestamp')[:10]

    context.update({
        'filter_date': filter_date,
        'search_query': search_query,
        'filter_type': filter_type,
        'meals_list': present_list,
        'away_list_consult': away_list_consult,
        'unconfirmed_count': unconfirmed_count,
        'chart_data_json': json.dumps(chart_data),
        'recent_activity': recent_activity,
    })

    return render(request, 'hms/admin/dashboard.html', context)

@login_required
@role_required(['Admin', 'Warden'])
def export_meals_csv(request):
    """Export confirmed meals to CSV"""
    
    import csv
    
    date_str = request.GET.get('date', str(date.today()))
    try:
        query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        query_date = date.today()
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="meals_{query_date}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'University ID', 'Breakfast', 'Early', 'Supper', 'Away', 'Phone'])
    
    meals = Meal.objects.filter(date=query_date).select_related('student__user')
    
    for meal in meals:
        writer.writerow([
            meal.student.user.get_full_name(),
            meal.student.university_id,
            'Yes' if meal.breakfast else 'No',
            'Yes' if meal.early else 'No',
            'Yes' if meal.supper else 'No',
            'Yes' if meal.away else 'No',
            meal.student.phone
        ])
        
    return response

@login_required
@role_required(['Admin', 'Finance'])
def manage_payments(request):
    """Admin view to manage/view all payments"""
    from django.db import models
    payments = Payment.objects.all().select_related('student__user').order_by('-created_at')
    
    # Simple filtering
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(status=status_filter)
        
    search_query = request.GET.get('q')
    if search_query:
        payments = payments.filter(
            models.Q(transaction_id__icontains=search_query) |
            models.Q(student__user__first_name__icontains=search_query) |
            models.Q(student__user__last_name__icontains=search_query) |
            models.Q(student__university_id__icontains=search_query)
        )

    context = {
        'payments': payments,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'hms/admin/manage_payments.html', context)

@login_required
@role_required(['Admin'])
def send_meal_notifications(request):
    """Send email notifications about unconfirmed students"""
    
    from django.core.mail import send_mail
    from django.conf import settings
    
    tomorrow = date.today() + timedelta(days=1)
    
    # Get all students
    all_students = Student.objects.all()
    
    # Get students who have confirmed meals for tomorrow
    confirmed_student_ids = Meal.objects.filter(
        date=tomorrow
    ).values_list('student_id', flat=True)
    
    # Find unconfirmed students
    unconfirmed_students = all_students.exclude(id__in=confirmed_student_ids)
    
    if not unconfirmed_students.exists():
        messages.success(request, '✅ All students have confirmed their meals for tomorrow!')
        return redirect('hms:admin_dashboard')
    
    # Prepare email content
    unconfirmed_count = unconfirmed_students.count()
    student_list = '\n'.join([
        f"  • {student.user.get_full_name()} ({student.university_id}) - {student.user.email}"
        for student in unconfirmed_students
    ])
    
    subject = f'⚠️ Meal Confirmation Alert - {unconfirmed_count} Students Unconfirmed for {tomorrow.strftime("%B %d, %Y")}'
    
    message = f"""
Hello Admin,

This is an automated notification from the Student Welfare Management System.

📅 Date: {tomorrow.strftime("%A, %B %d, %Y")}
⚠️ Unconfirmed Students: {unconfirmed_count} out of {all_students.count()}

The following students have NOT confirmed their meals for tomorrow:

{student_list}

Please remind these students to confirm their meal preferences before the deadline.

---
🔗 Access the admin dashboard: {request.build_absolute_uri('/kitchen/dashboard/')}

This is an automated message from Student Welfare Management System.
Do not reply to this email.
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        
        messages.success(
            request, 
            f'✅ Email notification sent successfully to {settings.ADMIN_EMAIL}! '
            f'{unconfirmed_count} unconfirmed students for {tomorrow.strftime("%B %d")}'
        )
        
    except Exception as e:
        messages.error(request, f'❌ Failed to send email: {str(e)}')
    
    return redirect('hms:admin_dashboard')

@login_required
@role_required(['Admin', 'Warden'])
def manage_students(request):
    """List and filter students (admin only)"""
    
    search_query = request.GET.get('search', '')
    residence_filter = request.GET.get('residence_type', '')
    status_filter = request.GET.get('status', '')
    
    students = Student.objects.all().select_related('user').order_by('user__first_name')
    
    if search_query:
        students = students.filter(
            models.Q(user__first_name__icontains=search_query) |
            models.Q(user__last_name__icontains=search_query) |
            models.Q(university_id__icontains=search_query)
        )
    
    if residence_filter:
        students = students.filter(residence_type=residence_filter)
        
    if status_filter == 'active':
        today = timezone.now().date()
        students = students.exclude(away_periods__start_date__lte=today, away_periods__end_date__gte=today)
    elif status_filter == 'away':
        today = timezone.now().date()
        students = students.filter(away_periods__start_date__lte=today, away_periods__end_date__gte=today).distinct()
    
    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'residence_filter': residence_filter,
        'status_filter': status_filter,
    }
    return render(request, 'hms/admin/manage_students.html', context)

@login_required
@role_required(['Admin', 'Warden'])
def add_student(request):
    """Add a new student (admin only)"""
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student added successfully!')
            return redirect('hms:manage_students')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'hms/registration/register.html', {'form': form, 'title': 'Add New Student'})

@login_required
@role_required(['Admin', 'Warden'])
def edit_student(request, user_id):
    """Edit student profile (admin only)"""
    
    user = get_object_or_404(User, id=user_id)
    student = get_object_or_404(Student, user=user)
    
    if request.method == 'POST':
        # Update user fields
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.username = request.POST.get('username', user.username) # Allow username edit
        user.save()
        
        # Update student fields
        student.university_id = request.POST.get('university_id', '')
        student.phone = request.POST.get('phone', '')
        student.room_number = request.POST.get('room_number', '')
        
        # New fields sync
        student.residence_type = request.POST.get('residence_type', 'hostel')
        student.hostel = request.POST.get('hostel') if request.POST.get('hostel') else None
        student.county = request.POST.get('county')
        student.gender = request.POST.get('gender')
        student.program_of_study = request.POST.get('program_of_study')
        student.disability = request.POST.get('disability', 'none')
        student.disability_details = request.POST.get('disability_details')

        student.is_away = request.POST.get('is_away') == 'on'
        student.is_warden = request.POST.get('is_warden') == 'on'
        student.save()
        
        messages.success(request, 'Student profile updated successfully!')
        return redirect('hms:manage_students')
    
    context = {
        'student': student,
        'residence_choices': Student.RESIDENCE_TYPE_CHOICES,
        'hostel_choices': Student.HOSTEL_CHOICES,
        'county_choices': Student.COUNTY_CHOICES,
        'gender_choices': Student.GENDER_CHOICES,
        'disability_choices': Student.DISABILITY_CHOICES,
    }
    
    return render(request, 'hms/admin/edit_student.html', context)

@login_required
@require_POST
@role_required(['Admin'])
def delete_student(request, user_id):
    """Delete student (admin only)"""
        
    user = get_object_or_404(User, id=user_id)
    student_name = user.get_full_name() or user.username
    user.delete()
    messages.success(request, f"Student '{student_name}' deleted successfully.")
    return redirect('hms:manage_students')

@login_required
@role_required(['Admin', 'Warden'])
def student_details(request, user_id):
    """View student details (admin only)"""
        
    user = get_object_or_404(User, id=user_id)
    student = get_object_or_404(Student, user=user)
    meal_history = student.meals.all().order_by('-date')[:15]
    
    return render(request, 'hms/admin/student_details.html', {
        'student': student,
        'meal_history': meal_history
    })

@login_required
@role_required(['Admin', 'Warden'])
def away_list(request):
    """View list of students currently away (admin only)"""
        
    today = date.today()
    away_periods = AwayPeriod.objects.filter(start_date__lte=today, end_date__gte=today).select_related('student__user')
    
    return render(request, 'hms/admin/students.html', {'students': [ap.student for ap in away_periods]})

# ==================== Announcements ====================

@login_required
def announcements_list(request):
    """View all announcements"""
    announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')
    context = {
        'announcements': announcements
    }
    return render(request, 'hms/student/announcements.html', context)

@login_required
@role_required(['Admin', 'Warden'])
def manage_announcements(request):
    """Manage announcements (admin only)"""
    
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    announcements = Announcement.objects.all().order_by('-created_at')
    
    if search_query:
        announcements = announcements.filter(
            models.Q(title__icontains=search_query) |
            models.Q(content__icontains=search_query)
        )
    
    if status_filter == 'active':
        announcements = announcements.filter(is_active=True)
    elif status_filter == 'inactive':
        announcements = announcements.filter(is_active=False)
        
    paginator = Paginator(announcements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'hms/admin/manage_announcements.html', context)

@login_required
@require_POST
@role_required(['Admin'])
def delete_announcement(request, pk):
    """Delete an announcement (admin only)"""
        
    announcement = get_object_or_404(Announcement, pk=pk)
    announcement_title = announcement.title
    announcement.delete()
    messages.success(request, f"News Alert '{announcement_title}' deleted successfully.")
    return redirect('hms:manage_announcements')

@login_required
@role_required(['Admin', 'Warden'])
def edit_announcement(request, pk):
    """Edit an announcement (admin only)"""
    announcement = get_object_or_404(Announcement, pk=pk)
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, "News Alert updated successfully.")
            return redirect('hms:manage_announcements')
    else:
        form = AnnouncementForm(instance=announcement)
        
    return render(request, 'hms/admin/announcement_form.html', {'form': form, 'announcement': announcement, 'edit_mode': True})


@login_required
@role_required(['Admin', 'Warden'])
def create_announcement(request):
    """Create new announcement"""
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            
            # Send notifications only if announcement is active
            if announcement.is_active:
                try:
                    from .notifications import notify_new_announcement
                    notify_new_announcement(announcement)
                    messages.success(request, 'News Alert created successfully and notifications sent!')
                except Exception as e:
                    messages.warning(request, f'News Alert created but notifications failed: {str(e)}')
            else:
                messages.success(request, 'Announcement created successfully (inactive - no notifications sent).')
            
            return redirect('hms:manage_announcements')
    else:
        form = AnnouncementForm()
    
    # GET request - show list of recent announcements (if needed by template)
    announcements = Announcement.objects.all().order_by('-created_at')[:10]
    return render(request, 'hms/admin/announcement_form.html', {
        'form': form,
        'announcements': announcements,
        'edit_mode': False
    })

# ==================== Activities ====================

@login_required
@role_required(['Admin', 'Warden'])
def activities_list(request):
    """View and manage all activities"""
    
    activities = Activity.objects.all().order_by('weekday', 'time')
    context = {
        'activities': activities
    }
    return render(request, 'hms/admin/activities.html', context)

@login_required
@role_required(['Admin', 'Warden'])
def create_activity(request):
    """Create a new activity"""
    
    if request.method == 'POST':
        display_name = request.POST.get('display_name', '')
        weekday = request.POST.get('weekday', 0)
        time_str = request.POST.get('time', '')
        description = request.POST.get('description', '')
        is_active = request.POST.get('active') == 'on'
        
        activity = Activity.objects.create(
            display_name=display_name,
            weekday=int(weekday),
            time=time_str if time_str else None,
            description=description,
            active=is_active
        )
        messages.success(request, f"Activity '{display_name}' created successfully!")
        return redirect('hms:activities')
    
    return render(request, 'hms/admin/activity_form.html', {'edit_mode': False})

@login_required
@role_required(['Admin', 'Warden'])
def edit_activity(request, pk):
    """Edit an existing activity"""
    
    activity = get_object_or_404(Activity, pk=pk)
    
    if request.method == 'POST':
        activity.display_name = request.POST.get('display_name', '')
        activity.weekday = int(request.POST.get('weekday', 0))
        time_str = request.POST.get('time', '')
        activity.time = time_str if time_str else None
        activity.description = request.POST.get('description', '')
        activity.active = request.POST.get('active') == 'on'
        activity.save()
        messages.success(request, f"Activity '{activity.display_name}' updated successfully!")
        return redirect('hms:activities')
    
    return render(request, 'hms/admin/activity_form.html', {'activity': activity, 'edit_mode': True})

@login_required
@require_POST
@role_required(['Admin'])
def delete_activity(request, pk):
    """Delete an activity"""
    
    activity = get_object_or_404(Activity, pk=pk)
    activity_name = activity.display_name
    activity.delete()
    messages.success(request, f"Activity '{activity_name}' deleted successfully!")
    return redirect('hms:activities')

@login_required
@role_required(['Admin', 'Warden'])
def toggle_activity_status(request, pk):
    """Toggle activity active status"""
    
    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('hms:activities')
    
    activity = get_object_or_404(Activity, pk=pk)
    activity.active = not activity.active
    activity.save()
    status = "activated" if activity.active else "deactivated"
    messages.success(request, f"Activity '{activity.display_name}' {status}!")
    return redirect('hms:activities')

# ==================== Additional Features ====================

@login_required
@role_required(['Admin', 'Warden'])
def upload_document(request):
    """Admin upload document"""
        
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Document uploaded successfully.")
            return redirect('hms:admin_dashboard')
    else:
        form = DocumentForm()
    return render(request, 'hms/admin/upload_document.html', {'form': form})

@login_required
def upload_timetable(request):
    """Student upload timetable"""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return redirect('hms:student_dashboard')
        
    if request.method == 'POST':
        form = TimetableForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Timetable uploaded successfully.")
            return redirect('hms:student_profile')
    return redirect('hms:student_profile')

@login_required
def select_room(request):
    """Student select room"""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return redirect('hms:student_dashboard')
        
    if request.method == 'POST':
        form = RoomSelectionForm(request.POST, instance=student)
        if form.is_valid():
            room_number = form.cleaned_data['room_number']
            
            # Find the room object
            try:
                room = Room.objects.get(room_number=room_number)
                
                # Check if already assigned to this room
                if student.room_number == room_number:
                    messages.info(request, f"You are already in Room {room_number}.")
                    return redirect('hms:student_profile')

                # Check availability (double check)
                if not room.is_available:
                     messages.error(request, f"Room {room_number} is not available.")
                     return redirect('hms:student_profile')
                     
                # Create Room Assignment
                # First, end any active assignments
                RoomAssignment.objects.filter(student=student, is_active=True).update(is_active=False, checkout_date=timezone.now())
                
                # Create new assignment
                RoomAssignment.objects.create(
                    student=student,
                    room=room,
                    bed_number=1, # Defaulting to 1 for now, logic can be enhanced
                    is_active=True
                )
                
                # Update student profile for display
                student.room_number = room_number
                student.save()
                
                messages.success(request, f"Successfully assigned to Room {room_number}.")
                
            except Room.DoesNotExist:
                messages.error(request, "Selected room does not exist.")
        else:
            messages.error(request, "Invalid room selection.")
            
    return redirect('hms:student_profile')

@login_required
def chat_view(request, recipient_id=None):
    """Chat interface"""
    if request.user.is_staff:
        # Admin view: List students ordered by latest message
        students = Student.objects.all().select_related('user')
        
        # Calculate unread counts and find latest message timestamp
        from django.db.models import Max
        for s in students:
            # Count unread messages from student to any staff member
            s.unread_count = Message.objects.filter(sender=s.user, recipient__is_staff=True, is_read=False).count()
            # Find latest interaction between this student and any staff member
            latest_msg = Message.objects.filter(
                (Q(sender=s.user) & Q(recipient__is_staff=True)) |
                (Q(sender__is_staff=True) & Q(recipient=s.user))
            ).order_by('-timestamp').first()
            
            s.latest_msg_time = latest_msg.timestamp if latest_msg else None
            s.latest_msg_content = latest_msg.content if latest_msg else ""
        
        # Sort students: those with unread messages first, then by latest message time
        # Students with no messages should be at the bottom, so we use a very old timestamp as fallback
        from datetime import datetime
        past_time = timezone.make_aware(datetime.min)
        students = sorted(students, key=lambda x: (x.unread_count > 0, x.latest_msg_time or past_time), reverse=True)

        if recipient_id:
             other_user = get_object_or_404(User, id=recipient_id)
        else:
             # Auto-select: Try to find student with unread messages first
             unread_student = next((s for s in students if getattr(s, 'unread_count', 0) > 0), None)
             
             if unread_student:
                 return redirect('hms:chat_with', recipient_id=unread_student.user.id)
             # Fallback: Select the first student in the list
             elif students:
                 return redirect('hms:chat_with', recipient_id=students[0].user.id)

             else:
                 other_user = None
    else:
        # Student view: Chat with Admin 
        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            messages.error(request, "No admin available to chat.")
            return redirect('hms:student_dashboard')
        other_user = admin_user
        students = None
        
    messages_qs = []
    if other_user:
        # If we are looking at a student's thread, show all staff communications with them
        if request.user.is_staff or (other_user.is_staff):
            student_user = other_user if request.user.is_staff else request.user
            messages_qs = Message.objects.filter(
                (Q(sender=student_user) & Q(recipient__is_staff=True)) |
                (Q(sender__is_staff=True) & Q(recipient=student_user))
            ).order_by('timestamp')
            
            # Mark messages from the student to ANY staff as read
            unread_messages = Message.objects.filter(recipient__is_staff=True, sender=student_user, is_read=False)
            if unread_messages.exists():
                unread_messages.update(is_read=True)
        else:
            # Fallback for non-staff related chats if they exist
            messages_qs = Message.objects.filter(
                (Q(sender=request.user) & Q(recipient=other_user)) |
                (Q(sender=other_user) & Q(recipient=request.user))
            ).order_by('timestamp')
            
            unread_messages = Message.objects.filter(recipient=request.user, sender=other_user, is_read=False)
            if unread_messages.exists():
                unread_messages.update(is_read=True)
        
        # Check online status: if student, check if ANY staff is online for "Staff Support"
        from django.core.cache import cache
        if not request.user.is_staff:
            any_staff_online = any(cache.get(f'seen_{u.id}') == 'online' for u in User.objects.filter(is_staff=True))
            is_online = any_staff_online
        else:
            is_online = cache.get(f'seen_{other_user.id}') == 'online'

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid() and other_user:
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.recipient = other_user
            msg.save()
            # Redirect to avoid form resubmission
            if request.user.is_staff:
                 return redirect('hms:chat_with', recipient_id=other_user.id)
            else:
                 return redirect('hms:chat')
            
    else:
        form = MessageForm()
        
    context = {
        'other_user': other_user,
        'messages': messages_qs,
        'form': form,
        'students': students,
        'is_online': is_online if other_user else False,
    }
    return render(request, 'hms/chat.html', context)

@login_required
def clear_chat(request, recipient_id):
    """Deletes all messages between the current user and the recipient"""
    other_user = get_object_or_404(User, id=recipient_id)
    
    # Delete messages in both directions
    Message.objects.filter(
        (Q(sender=request.user) & Q(recipient=other_user)) |
        (Q(sender=other_user) & Q(recipient=request.user))
    ).delete()
    
    from django.contrib import messages as django_messages
    django_messages.success(request, f"Conversation with {other_user.get_full_name() or other_user.username} has been cleared.")
    
    # Redirect back to the chat view
    if request.user.is_staff:
        return redirect('hms:chat_with', recipient_id=recipient_id)
    else:
        return redirect('hms:chat')

# ==================== Maintenance Requests ====================

@login_required
def submit_maintenance_request(request):
    """View for students to submit a maintenance ticket"""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('hms:student_dashboard')

    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST, request.FILES)
        if form.is_valid():
            maintenance_request = form.save(commit=False)
            maintenance_request.student = student
            maintenance_request.save()
            messages.success(request, 'Maintenance request submitted successfully!')
            return redirect('hms:student_maintenance_list')
    else:
        form = MaintenanceRequestForm()
    
    return render(request, 'hms/student/maintenance_form.html', {'form': form})

@login_required
def student_maintenance_list(request):
    """View for students to see their maintenance tickets"""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
         return redirect('hms:student_dashboard')

    requests = MaintenanceRequest.objects.filter(student=student).order_by('-created_at')
    
    return render(request, 'hms/student/maintenance_list.html', {'requests': requests})

@login_required
@require_POST
def delete_maintenance_request(request, pk):
    """Student deletes their pending maintenance request"""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
         return redirect('hms:student_dashboard')

    maintenance_req = get_object_or_404(MaintenanceRequest, pk=pk, student=student)
    
    if maintenance_req.status != 'pending':
        messages.error(request, "Cannot delete request that is already in progress or resolved.")
        return redirect('hms:student_maintenance_list')
        
    maintenance_req.delete()
    messages.success(request, "Maintenance request cancelled successfully.")
    
    return redirect('hms:student_maintenance_list')

@login_required
@role_required(['Admin', 'Warden'])
def manage_maintenance(request):
    """Admin view to manage maintenance tickets"""
        
    requests = MaintenanceRequest.objects.all().select_related('student__user').order_by(
        models.Case(
            models.When(status='pending', then=0),
            models.When(status='in_progress', then=1),
            models.When(status='resolved', then=2),
            default=3,
        ),
        '-created_at'
    )
    
    return render(request, 'hms/admin/maintenance_list.html', {'requests': requests})

@login_required
@role_required(['Admin', 'Warden'])
def update_maintenance_status(request, pk):
    """Admin view to update status of a ticket"""
         
    maintenance_request = get_object_or_404(MaintenanceRequest, pk=pk)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(MaintenanceRequest.STATUS_CHOICES):
            maintenance_request.status = status
            maintenance_request.save()
            
            # Send notification
            from .notifications import notify_maintenance_status_update
            notify_maintenance_status_update(maintenance_request)
            
            messages.success(request, f"Status updated to {maintenance_request.get_status_display()}")
        
    return redirect('hms:manage_maintenance')


# ==================== ROOM MANAGEMENT ====================

@login_required
@role_required(['Admin', 'Warden'])
def room_list(request):
    """View all rooms (admin only)"""
    
    rooms = Room.objects.all().order_by('block', 'floor', 'room_number')
    
    # Filter by block if provided
    block_filter = request.GET.get('block')
    if block_filter:
        rooms = rooms.filter(block__icontains=block_filter)
    
    # Filter by availability
    availability = request.GET.get('availability')
    if availability == 'available':
        rooms = rooms.filter(is_available=True)
    elif availability == 'occupied':
        rooms = rooms.filter(is_available=False)
    
    context = {
        'rooms': rooms,
        'total_rooms': Room.objects.count(),
        'available_rooms': Room.objects.filter(is_available=True).count(),
        'occupied_rooms': Room.objects.filter(is_available=False).count(),
    }
    
    return render(request, 'hms/admin/room_list.html', context)


@login_required
@role_required(['Admin'])
def create_room(request):
    """Create a new room (admin only)"""
    from .forms import RoomForm
    
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room created successfully!')
            return redirect('hms:room_list')
    else:
        form = RoomForm()
    
    return render(request, 'hms/admin/room_form.html', {'form': form, 'action': 'Create'})


@login_required
@role_required(['Admin'])
def edit_room(request, pk):
    """Edit room details (admin only)"""
    from .forms import RoomForm
    
    room = get_object_or_404(Room, pk=pk)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room updated successfully!')
            return redirect('hms:room_list')
    else:
        form = RoomForm(instance=room)
    
    return render(request, 'hms/admin/room_form.html', {'form': form, 'action': 'Edit', 'room': room})


@login_required
@require_POST
@role_required(['Admin'])
def delete_room(request, pk):
    """Delete a room (admin only)"""
    
    room = get_object_or_404(Room, pk=pk)
    room_number = room.room_number
    room.delete()
    messages.success(request, f'Room {room_number} deleted successfully!')
    return redirect('hms:room_list')


@login_required
@role_required(['Admin', 'Warden'])
def room_assignments(request):
    """View all room assignments (admin only)"""
    
    assignments = RoomAssignment.objects.filter(is_active=True).select_related('student__user', 'room')
    
    context = {
        'assignments': assignments,
        'total_assigned': assignments.count(),
    }
    
    return render(request, 'hms/admin/room_assignments.html', context)


@login_required
@role_required(['Admin', 'Warden'])
def assign_room(request):
    """Assign a student to a room (admin only)"""
    from .forms import RoomAssignmentForm
    
    if request.method == 'POST':
        form = RoomAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            
            # Check if room has available beds
            room = assignment.room
            if room.available_beds <= 0:
                messages.error(request, f'Room {room.room_number} is full!')
                return render(request, 'hms/admin/room_assignment_form.html', {'form': form})
            
            assignment.save()
            
            # Update student's room_number field
            student = assignment.student
            student.room_number = room.room_number
            student.save()
            
            messages.success(request, f'{student.user.get_full_name()} assigned to Room {room.room_number}!')
            return redirect('hms:room_assignments')
    else:
        form = RoomAssignmentForm()
    
    return render(request, 'hms/admin/room_assignment_form.html', {'form': form})


@login_required
@role_required(['Admin', 'Warden'])
def room_change_requests(request):
    """View all room change requests (admin only)"""
    
    requests_list = RoomChangeRequest.objects.all().select_related('student__user', 'current_room', 'requested_room')
    
    context = {
        'change_requests': requests_list,
        'pending_count': requests_list.filter(status='pending').count(),
    }
    
    return render(request, 'hms/admin/room_change_requests.html', context)


@login_required
@role_required(['Admin', 'Warden'])
def approve_room_change(request, pk):
    """Approve/reject a room change request (admin only)"""
    
    room_change = get_object_or_404(RoomChangeRequest, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_notes = request.POST.get('admin_notes', '')
        
        if action == 'approve':
            room_change.status = 'approved'
            room_change.admin_notes = admin_notes
            room_change.reviewed_by = request.user
            room_change.save()
            
            # Create new assignment if there's a requested room
            if room_change.requested_room:
                # Deactivate old assignment
                RoomAssignment.objects.filter(student=room_change.student, is_active=True).update(is_active=False, checkout_date=timezone.now().date())
                
                # Create new assignment
                RoomAssignment.objects.create(
                    student=room_change.student,
                    room=room_change.requested_room,
                    assigned_date=timezone.now().date(),
                    is_active=True
                )
                
                # Update student's room_number
                room_change.student.room_number = room_change.requested_room.room_number
                room_change.student.save()
            
            messages.success(request, f'Room change request approved for {room_change.student.user.get_full_name()}!')
        
        elif action == 'reject':
            room_change.status = 'rejected'
            room_change.admin_notes = admin_notes
            room_change.reviewed_by = request.user
            room_change.save()
            messages.info(request, 'Room change request rejected.')
        
        return redirect('hms:room_change_requests')
    
    return render(request, 'hms/admin/approve_room_change.html', {'room_change': room_change})


@login_required
def student_request_room_change(request):
    """Student submits a room change request"""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('hms:student_dashboard')
    
    from .forms import RoomChangeRequestForm
    
    # Get student's current room
    current_assignment = RoomAssignment.objects.filter(student=student, is_active=True).first()
    
    if request.method == 'POST':
        form = RoomChangeRequestForm(request.POST)
        if form.is_valid():
            room_change = form.save(commit=False)
            room_change.student = student
            room_change.current_room = current_assignment.room if current_assignment else None
            room_change.save()
            
            messages.success(request, 'Room change request submitted successfully!')
            return redirect('hms:student_dashboard')
    else:
        form = RoomChangeRequestForm()
    
    context = {
        'form': form,
        'current_room': current_assignment.room if current_assignment else None,
    }
    
    return render(request, 'hms/student/room_change_request_form.html', context)


# ==================== LEAVE REQUESTS ====================

@login_required
def submit_leave_request(request):
    """Student submits a leave request"""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('hms:student_dashboard')
    
    from .forms import LeaveRequestForm
    
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, request.FILES)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.student = student
            leave_request.save()
            
            # Notify admin
            from .notifications import notify_deferment_request_submitted
            notify_deferment_request_submitted(leave_request)
            
            messages.success(request, 'Leave request submitted successfully! Awaiting approval.')
            return redirect('hms:student_leave_list')
    else:
        form = LeaveRequestForm()
    
    return render(request, 'hms/student/leave_request_form.html', {'form': form})


@login_required
def student_leave_list(request):
    """Student views their leave requests"""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('hms:student_dashboard')
    
    leave_requests = LeaveRequest.objects.filter(student=student).order_by('-created_at')
    
    context = {
        'leave_requests': leave_requests,
        'pending_count': leave_requests.filter(status='pending').count(),
    }
    
    return render(request, 'hms/student/leave_list.html', context)

@login_required
@require_POST
def delete_leave_request(request, pk):
    """Student cancels their pending leave request"""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('hms:student_dashboard')
    
    leave_req = get_object_or_404(LeaveRequest, pk=pk, student=student)
    
    if leave_req.status != 'pending':
        messages.error(request, "Cannot cancel leave request that has already been processed.")
        return redirect('hms:student_leave_list')
        
    leave_req.delete()
    messages.success(request, "Leave request cancelled successfully.")
        
    return redirect('hms:student_leave_list')


# ========== DEFERMENT MANAGEMENT VIEWS ==========

@login_required
@role_required(['Admin', 'Warden'])
def admin_deferment_all(request):
    """Admin views all deferment requests"""
    
    deferments = DefermentRequest.objects.all().select_related('student__user').order_by('-created_at')
    
    context = {
        'deferments': deferments,
        'title': 'All Deferment Requests',
        'active_tab': 'all'
    }
    return render(request, 'hms/admin/deferment_list.html', context)

@login_required
@role_required(['Admin', 'Warden'])
def admin_deferment_pending(request):
    """Admin views pending deferment requests"""
    
    deferments = DefermentRequest.objects.filter(status='pending').select_related('student__user').order_by('-created_at')
    
    context = {
        'deferments': deferments,
        'title': 'Pending Applications',
        'active_tab': 'pending'
    }
    return render(request, 'hms/admin/deferment_list.html', context)

@login_required
@role_required(['Admin', 'Warden'])
def admin_deferment_under_review(request):
    """Admin views deferment requests under review"""
    
    deferments = DefermentRequest.objects.filter(status='under_review').select_related('student__user').order_by('-created_at')
    
    context = {
        'deferments': deferments,
        'title': 'Applications Under Review',
        'active_tab': 'under_review'
    }
    return render(request, 'hms/admin/deferment_list.html', context)

@login_required
def admin_deferment_approved(request):
    """Admin views approved deferment requests"""
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin only.")
        return redirect('hms:student_dashboard')
    
    deferments = DefermentRequest.objects.filter(status='approved').select_related('student__user').order_by('-created_at')
    
    context = {
        'deferments': deferments,
        'title': 'Approved Deferments',
        'active_tab': 'approved'
    }
    return render(request, 'hms/admin/deferment_list.html', context)

@login_required
def admin_deferment_rejected(request):
    """Admin views rejected deferment requests"""
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin only.")
        return redirect('hms:student_dashboard')
    
    deferments = DefermentRequest.objects.filter(status='rejected').select_related('student__user').order_by('-created_at')
    
    context = {
        'deferments': deferments,
        'title': 'Rejected Applications',
        'active_tab': 'rejected'
    }
    return render(request, 'hms/admin/deferment_list.html', context)

@login_required
@role_required(['Admin', 'Warden'])
def admin_deferment_resumed(request):
    """Admin views resumed studies deferment requests"""
    
    deferments = DefermentRequest.objects.filter(status='resumed').select_related('student__user').order_by('-created_at')
    
    context = {
        'deferments': deferments,
        'title': 'Resumed Studies',
        'active_tab': 'resumed'
    }
    return render(request, 'hms/admin/deferment_list.html', context)

@login_required
@role_required(['Admin', 'Warden'])
def review_deferment(request, pk):
    """Admin approves/rejects/updates a deferment request"""
    
    from .forms import DefermentApprovalForm
    
    deferment = get_object_or_404(DefermentRequest, pk=pk)
    
    if request.method == 'POST':
        form = DefermentApprovalForm(request.POST, instance=deferment)
        if form.is_valid():
            defer_req = form.save(commit=False)
            defer_req.reviewed_by = request.user
            defer_req.reviewed_at = timezone.now()
            defer_req.save()
            
            # If approved, create AwayPeriod automatically
            if defer_req.status == 'approved':
                AwayPeriod.objects.create(
                    student=defer_req.student,
                    start_date=defer_req.start_date,
                    end_date=defer_req.end_date
                )
                messages.success(request, f'Deferment approved for {defer_req.student.user.get_full_name()}. Away period created.')
            else:
                messages.info(request, f'Deferment status updated to {defer_req.get_status_display()}.')
            
            # Notify student
            from .notifications import notify_deferment_status
            notify_deferment_status(defer_req)
            
            # Redirect back to the list of the updated status
            if defer_req.status == 'pending':
                return redirect('hms:admin_deferment_pending')
            elif defer_req.status == 'under_review':
                return redirect('hms:admin_deferment_under_review')
            elif defer_req.status == 'approved':
                return redirect('hms:admin_deferment_approved')
            elif defer_req.status == 'rejected':
                return redirect('hms:admin_deferment_rejected')
            elif defer_req.status == 'resumed':
                return redirect('hms:admin_deferment_resumed')
            else:
                return redirect('hms:admin_deferment_all')
                
    else:
        form = DefermentApprovalForm(instance=deferment)
    
    return render(request, 'hms/admin/review_deferment.html', {'form': form, 'deferment': deferment})


# Maintain alias for compatibility with old URLs if needed
manage_leave_requests = admin_deferment_all
approve_leave_request = review_deferment


# ==================== ANALYTICS DASHBOARD ====================

@login_required
@role_required(['Admin', 'Warden', 'Finance'])
def analytics_dashboard(request):
    """Comprehensive analytics dashboard for admins"""
    
    import json
    from django.db.models import Count, Q
    from django.db.models.functions import TruncDate
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today - timedelta(days=29)
    
    # ==================== SUMMARY STATS ====================
    total_students = Student.objects.count()
    total_rooms = Room.objects.count()
    available_rooms = Room.objects.filter(is_available=True).count()
    
    # Today's meal stats
    today_meals = Meal.objects.filter(date=today)
    today_breakfast = today_meals.filter(breakfast=True).count()
    today_supper = today_meals.filter(supper=True).count()
    today_away = today_meals.filter(away=True).count()
    today_confirmed = today_meals.count()
    
    # Active leave requests
    active_leaves = LeaveRequest.objects.filter(
        status='approved',
        start_date__lte=today,
        end_date__gte=today
    ).count()
    
    # Pending items
    pending_maintenance = MaintenanceRequest.objects.filter(status='pending').count()
    pending_leaves = LeaveRequest.objects.filter(status='pending').count()
    
    # ==================== DATA AGGREGATION HELPER ====================
    def get_counts_for_dates(queryset, date_field, dates):
        from django.db.models.functions import TruncDate
        counts = queryset.filter(**{f"{date_field}__date__in": dates}) \
                         .annotate(day=TruncDate(date_field)) \
                         .values('day') \
                         .annotate(count=Count('id'))
        mapping = {item['day']: item['count'] for item in counts}
        return [mapping.get(d, 0) for d in dates]

    # Date ranges
    weekly_dates = [week_start + timedelta(days=i) for i in range(7)]
    monthly_dates = [month_start + timedelta(days=i) for i in range(30)]

    # Weekly Trends
    weekly_labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekly_registrations = get_counts_for_dates(Student.objects, 'user__date_joined', weekly_dates)
    weekly_payments = get_counts_for_dates(Payment.objects.filter(status='Completed'), 'created_at', weekly_dates)
    weekly_maintenance = get_counts_for_dates(MaintenanceRequest.objects, 'created_at', weekly_dates)
    weekly_visitors = get_counts_for_dates(Visitor.objects, 'check_in_time', weekly_dates)
    weekly_deferments = get_counts_for_dates(DefermentRequest.objects, 'created_at', weekly_dates)
    
    # Weekly Meals (Special handled)
    meal_stats = Meal.objects.filter(date__in=weekly_dates)
    weekly_breakfast = []
    weekly_supper = []
    weekly_away = []
    for d in weekly_dates:
        day_meals = meal_stats.filter(date=d)
        weekly_breakfast.append(day_meals.filter(breakfast=True).count())
        weekly_supper.append(day_meals.filter(supper=True).count())
        weekly_away.append(day_meals.filter(away=True).count())

    # Monthly Trends
    monthly_labels = [d.strftime('%b %d') for d in monthly_dates]
    monthly_registrations = get_counts_for_dates(Student.objects, 'user__date_joined', monthly_dates)
    monthly_payments = get_counts_for_dates(Payment.objects.filter(status='Completed'), 'created_at', monthly_dates)
    monthly_maintenance = get_counts_for_dates(MaintenanceRequest.objects, 'created_at', monthly_dates)
    monthly_visitors = get_counts_for_dates(Visitor.objects, 'check_in_time', monthly_dates)
    monthly_deferments = get_counts_for_dates(DefermentRequest.objects, 'created_at', monthly_dates)
    
    # Monthly Meals
    monthly_meal_stats = Meal.objects.filter(date__in=monthly_dates)
    monthly_breakfast = []
    monthly_supper = []
    monthly_away = []
    for d in monthly_dates:
        day_meals = monthly_meal_stats.filter(date=d)
        monthly_breakfast.append(day_meals.filter(breakfast=True).count())
        monthly_supper.append(day_meals.filter(supper=True).count())
        monthly_away.append(day_meals.filter(away=True).count())
    
    # ==================== MAINTENANCE STATS ====================
    maintenance_by_status = {
        'pending': MaintenanceRequest.objects.filter(status='pending').count(),
        'in_progress': MaintenanceRequest.objects.filter(status='in_progress').count(),
        'resolved': MaintenanceRequest.objects.filter(status__in=['resolved', 'completed']).count(),
    }
    
    maintenance_by_priority = {
        'low': MaintenanceRequest.objects.filter(priority='low').count(),
        'medium': MaintenanceRequest.objects.filter(priority='medium').count(),
        'high': MaintenanceRequest.objects.filter(priority='high').count(),
        'critical': MaintenanceRequest.objects.filter(priority='critical').count(),
    }
    
    # ==================== LEAVE REQUEST STATS ====================
    leave_by_status = {
        'pending': DefermentRequest.objects.filter(status='pending').count(),
        'approved': DefermentRequest.objects.filter(status='approved').count(),
        'rejected': DefermentRequest.objects.filter(status='rejected').count(),
    }
    
    leave_by_type = {}
    for leave_type_code, leave_type_name in DefermentRequest.DEFERMENT_TYPES:
        leave_by_type[leave_type_name] = DefermentRequest.objects.filter(deferment_type=leave_type_code).count()
    
    # ==================== ROOM OCCUPANCY ====================
    room_stats = {
        'total': total_rooms,
        'available': available_rooms,
        'occupied': total_rooms - available_rooms,
        'occupancy_rate': round((total_rooms - available_rooms) / total_rooms * 100, 1) if total_rooms > 0 else 0
    }
    
    # Room by type
    room_by_type = {}
    for room_type_code, room_type_name in Room.ROOM_TYPES:
        room_by_type[room_type_name] = Room.objects.filter(room_type=room_type_code).count()
    
    # ==================== RECENT ACTIVITY ====================
    recent_maintenance = MaintenanceRequest.objects.select_related('student__user').order_by('-created_at')[:5]
    recent_leaves = DefermentRequest.objects.select_related('student__user').order_by('-created_at')[:5]
    recent_announcements = Announcement.objects.order_by('-created_at')[:5]
    
    # ==================== CHART DATA JSON ====================
    chart_data = {
        'weekly': {
            'labels': weekly_labels,
            'registrations': weekly_registrations,
            'payments': weekly_payments,
            'maintenance': weekly_maintenance,
            'visitors': weekly_visitors,
            'deferments': weekly_deferments,
            'breakfast': weekly_breakfast,
            'supper': weekly_supper,
            'away': weekly_away,
        },
        'monthly': {
            'labels': monthly_labels,
            'registrations': monthly_registrations,
            'payments': monthly_payments,
            'maintenance': monthly_maintenance,
            'visitors': monthly_visitors,
            'deferments': monthly_deferments,
            'breakfast': monthly_breakfast,
            'supper': monthly_supper,
            'away': monthly_away,
        },
        'maintenance_status': maintenance_by_status,
        'maintenance_priority': maintenance_by_priority,
        'leave_status': leave_by_status,
        'leave_type': leave_by_type,
        'room_occupancy': room_stats,
    }
    
    context = {
        'today': today,
        # Summary stats
        'total_students': total_students,
        'today_breakfast': today_breakfast,
        'today_supper': today_supper,
        'today_away': today_away,
        'today_confirmed': today_confirmed,
        'active_leaves': active_leaves,
        'pending_maintenance': pending_maintenance,
        'pending_leaves': pending_leaves,
        # Room stats
        'room_stats': room_stats,
        'room_by_type': room_by_type,
        # Recent activity
        'recent_maintenance': recent_maintenance,
        'recent_leaves': recent_leaves,
        'recent_announcements': recent_announcements,
        # Chart data
        'chart_data_json': json.dumps(chart_data),
        'leave_by_type': leave_by_type,
    }
    
    return render(request, 'hms/admin/analytics_dashboard.html', context)


@login_required
def visitor_management(request):
    """View to list active visitors and check them in/out"""
    # Only staff can manage visitors
    if not request.user.is_staff and not request.user.student_profile.is_warden:
        messages.error(request, "You do not have permission to access visitor management.")
        return redirect('hms:student_dashboard')
    
    # Handle Check-In Form Submission
    if request.method == 'POST':
        form = VisitorForm(request.POST)
        if form.is_valid():
            visitor = form.save(commit=False)
            visitor.created_by = request.user
            visitor.save()
            messages.success(request, f"Visitor {visitor.name} checked in successfully.")
            return redirect('hms:visitor_management')
    else:
        form = VisitorForm()
    
    # Get active visitors
    active_visitors = Visitor.objects.filter(is_active=True).order_by('-check_in_time')
    
    # Get recent history (limited to 50 for performance)
    visitor_history = Visitor.objects.filter(is_active=False).order_by('-check_out_time')[:50]
    
    context = {
        'form': form,
        'active_visitors': active_visitors,
        'visitor_history': visitor_history,
    }
    
    return render(request, 'hms/admin/visitor_management.html', context)

@login_required
def checkout_visitor(request, visitor_id):
    """View to check out a visitor"""
    if not request.user.is_staff and not request.user.student_profile.is_warden:
        messages.error(request, "Permission denied.")
        return redirect('hms:student_dashboard')
        
    visitor = get_object_or_404(Visitor, id=visitor_id)
    
    if visitor.is_active:
        visitor.check_out()
        messages.success(request, f"Visitor {visitor.name} has been checked out.")
    else:
        messages.warning(request, "Visitor is already checked out.")
        
    return redirect('hms:visitor_management')


# ==================== Payment & M-Pesa ====================

@login_required
def pay_accommodation(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')
        
        # Basic validation
        if not phone or not amount:
            messages.error(request, "Please provide phone number and amount")
            return redirect('hms:pay_accommodation')

        # Save pending payment
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            messages.error(request, "Student profile not found.")
            return redirect('hms:dashboard')

        payment = Payment.objects.create(
            student=student,
            amount=amount,
            phone_number=phone,
            status='Pending'
        )
        
        # Initiate STK Push
        mpesa = MpesaClient()
        # Ensure callback URL is accessible from internet (e.g. ngrok) for local dev
        callback_url = settings.MPESA_CALLBACK_URL
        response = mpesa.stk_push(phone, amount, "Accommodation", callback_url)
        
        if response.get('ResponseCode') == '0':
            payment.checkout_request_id = response.get('CheckoutRequestID')
            payment.save()
            messages.success(request, f"STK Push initiated to {phone}. Check your phone to complete payment.")
        else:
            payment.status = 'Failed'
            payment.description = response.get('ResponseDescription', 'Unknown Error')
            payment.save()
            messages.error(request, f"Payment initiation failed: {payment.description}")
            
        return redirect('hms:payment_history')
        
    return render(request, 'hms/student/pay_accommodation.html')

@login_required
def payment_history(request):
    try:
        student = request.user.student_profile
        payments = Payment.objects.filter(student=student).order_by('-created_at')
    except Student.DoesNotExist:
        payments = []
    return render(request, 'hms/student/payment_history.html', {'payments': payments})

@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Log raw data for debugging if needed
            # print(data)
            
            stk_callback = data.get('Body', {}).get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            result_desc = stk_callback.get('ResultDesc')
            
            if not checkout_request_id:
                return JsonResponse({'status': 'error', 'message': 'No CheckoutRequestID'}, status=400)

            try:
                payment = Payment.objects.get(checkout_request_id=checkout_request_id)
            except Payment.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Payment not found'}, status=404)

            if result_code == 0:
                payment.status = 'Completed'
                payment.description = 'Success'
                # Extract receipt no
                meta = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                for item in meta:
                    if item.get('Name') == 'MpesaReceiptNumber':
                        payment.transaction_id = item.get('Value')
                
                # Send Notification
                Notification.objects.create(
                    user=payment.student.user,
                    title="Payment Received",
                    message=f"We received your payment of KES {payment.amount}. Ref: {payment.transaction_id}",
                    link="/student/payment-history/"
                )
            else:
                payment.status = 'Failed'
                payment.description = result_desc

            payment.save()
        except Exception as e:
            print(f"Callback Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'only post'}, status=400)

@login_required
def check_payment_status(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, student=request.user.student_profile)
    
    if payment.status == 'Completed':
        messages.info(request, "Payment is already completed.")
        return redirect('hms:payment_history')
        
    if not payment.checkout_request_id:
        messages.error(request, "Cannot verify this payment (No CheckoutRequestID).")
        return redirect('hms:payment_history')

    mpesa = MpesaClient()
    response = mpesa.stk_push_query(payment.checkout_request_id)
    
    if response.get('ResponseCode') == '0':
        result_code = response.get('ResultCode')
        if result_code == '0':
            payment.status = 'Completed'
            payment.description = response.get('ResultDesc', 'Verified Manually')
            payment.save()
            
            Notification.objects.create(
                user=request.user, 
                title="Payment Verified",
                message=f"Manual verification successful for KES {payment.amount}.",
                link="/student/payment-history/"
            )
            
            messages.success(request, "Payment verified successfully!")
        else:
            if result_code in ['1032', '1037', '1']:
                payment.status = 'Failed'
                payment.description = response.get('ResultDesc')
                payment.save()
            messages.warning(request, f"Payment status: {response.get('ResultDesc')}")
    else:
        messages.error(request, f"Query failed: {response.get('ResponseDescription', response.get('errorMessage'))}")
        
    return redirect('hms:payment_history')


# ==================== Global Search ====================

@login_required
def global_search(request):
    """
    Global search across all modules:
    - Students (name, email, university_id)
    - Announcements (title, content)
    - Maintenance Requests (description, location)
    - Deferment Requests (reason)
    """
    query = request.GET.get('q', '').strip()
    
    results = {
        'students': [],
        'announcements': [],
        'maintenance': [],
        'deferments': [],
        'query': query,
        'total_count': 0
    }
    
    if query and len(query) >= 2:
        # Search Students (admin only)
        if request.user.is_staff:
            students = Student.objects.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(university_id__icontains=query) |
                Q(phone__icontains=query)
            ).select_related('user')[:10]
            results['students'] = students
        
        # Search Announcements
        announcements = Announcement.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query),
            is_active=True
        ).order_by('-created_at')[:10]
        results['announcements'] = announcements
        
        # Search Maintenance Requests
        if request.user.is_staff:
            maintenance = MaintenanceRequest.objects.filter(
                Q(description__icontains=query) |
                Q(location__icontains=query)
            ).select_related('student__user').order_by('-created_at')[:10]
        else:
            # Students can only see their own requests
            try:
                student = request.user.student_profile
                maintenance = MaintenanceRequest.objects.filter(
                    Q(description__icontains=query) |
                    Q(location__icontains=query),
                    student=student
                ).order_by('-created_at')[:10]
            except:
                maintenance = []
        results['maintenance'] = maintenance
        
        # Search Deferment Requests
        if request.user.is_staff:
            deferments = DefermentRequest.objects.filter(
                Q(reason__icontains=query) |
                Q(student__user__first_name__icontains=query) |
                Q(student__user__last_name__icontains=query)
            ).select_related('student__user').order_by('-created_at')[:10]
        else:
            try:
                student = request.user.student_profile
                deferments = DefermentRequest.objects.filter(
                    Q(reason__icontains=query),
                    student=student
                ).order_by('-created_at')[:10]
            except:
                deferments = []
        results['deferments'] = deferments
        
        # Calculate total
        results['total_count'] = (
            len(results['students']) + 
            len(results['announcements']) + 
            len(results['maintenance']) + 
            len(results['deferments'])
        )
    
    return render(request, 'hms/search_results.html', results)

# ==================== Audit Logs ====================

@login_required
@role_required(['Admin', 'Finance'])
def audit_log_list(request):
    """
    Admin/Finance view for Audit Logs.
    Includes filtering, search, and pagination.
    """
    from django.core.paginator import Paginator
    
    logs = AuditLog.objects.all().select_related('user')
    
    # Search
    query = request.GET.get('q', '').strip()
    if query:
        logs = logs.filter(
            Q(user__username__icontains=query) |
            Q(object_repr__icontains=query) |
            Q(details__icontains=query) |
            Q(ip_address__icontains=query)
        )
        
    # Filter by Action
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)
        
    # Filter by Model
    model = request.GET.get('model')
    if model:
        logs = logs.filter(model_name=model)
        
    # Pagination
    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Unique values for filters
    unique_actions = AuditLog.objects.exclude(action__exact='').values_list('action', flat=True).distinct().order_by('action')
    unique_models = AuditLog.objects.exclude(model_name__isnull=True).values_list('model_name', flat=True).distinct().order_by('model_name')
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'current_action': action,
        'current_model': model,
        'unique_actions': unique_actions,
        'unique_models': unique_models,
    }
    return render(request, 'hms/admin/audit_logs.html', context)

@login_required
@role_required(['Admin', 'Finance'])
def audit_log_export(request):
    """
    Export Audit Logs to CSV based on current filters.
    """
    import csv
    from django.http import HttpResponse
    
    logs = AuditLog.objects.all().select_related('user')
    
    # Apply same filters as list view
    query = request.GET.get('q', '').strip()
    if query:
        logs = logs.filter(
            Q(user__username__icontains=query) |
            Q(object_repr__icontains=query) |
            Q(details__icontains=query) |
            Q(ip_address__icontains=query)
        )
        
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)
        
    model = request.GET.get('model')
    if model:
        logs = logs.filter(model_name=model)
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="audit_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'User', 'Role', 'Action', 'Model', 'Object ID', 'Object Repr', 'Details', 'IP Address'])
    
    for log in logs:
        user_role = "System"
        if log.user:
            if log.user.is_superuser:
                user_role = "Superuser"
            elif hasattr(log.user, 'student_profile') and log.user.student_profile.is_warden:
                user_role = "Warden" 
            else:
                user_role = "Student"
                
        writer.writerow([
            log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            log.user.username if log.user else "System",
            user_role,
            log.action,
            log.model_name,
            log.object_id,
            log.object_repr,
            log.details,
            log.ip_address
        ])
        
    return response


@login_required
def update_student_status(request):
    """Toggle student status (attachment/graduating)"""
    if request.method == 'POST':
        try:
            student = request.user.student_profile
            
            # Check which toggle was clicked
            if 'toggle_attachment' in request.POST:
                student.is_on_attachment = not student.is_on_attachment
                # If on attachment, they might be away? (Optional logic)
                status = "ON ATTACHMENT" if student.is_on_attachment else "OFF ATTACHMENT"
                messages.success(request, f'Status updated: You are now {status}.')
                
            elif 'toggle_graduating' in request.POST:
                student.is_graduating = not student.is_graduating
                status = "GRADUATING CLASS" if student.is_graduating else "CONTINUING STUDENT"
                messages.success(request, f'Status updated: You are now marked as {status}.')
                
            student.save()
            
        except AttributeError:
            messages.error(request, "Student profile not found.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            
            
    return redirect('hms:student_dashboard')


# ==================== LOST AND FOUND ====================

@login_required
def lost_found_list(request):
    """List all lost and found items"""
    status_filter = request.GET.get('status', 'ALL')
    query = request.GET.get('q', '')
    
    items = LostItem.objects.all().select_related('reported_by')
    
    if status_filter != 'ALL':
        if status_filter == 'RESOLVED':
            items = items.filter(status='CLAIMED')
        else:
            items = items.filter(status=status_filter)
            
    if query:
        items = items.filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(location__icontains=query)
        )
        
    context = {
        'items': items,
        'status_filter': status_filter,
        'query': query,
    }
    return render(request, 'hms/lost_found/list.html', context)

@login_required
def report_lost_item(request):
    """Report a new lost or found item"""
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.reported_by = request.user
            item.save()
            messages.success(request, 'Item reported successfully.')
            return redirect('hms:lost_found_list')
    else:
        form = LostItemForm()
        
    return render(request, 'hms/lost_found/form.html', {'form': form})

@login_required
def resolve_item(request, item_id):
    """Mark item as claimed/resolved"""
    item = get_object_or_404(LostItem, id=item_id)
    
    # Only reporter or staff can resolve
    if request.user == item.reported_by or request.user.is_staff:
        item.status = 'CLAIMED'
        item.save()
        messages.success(request, 'Item marked as resolved.')
    else:
        messages.error(request, 'You do not have permission to resolve this item.')
        
    return redirect('hms:lost_found_list')