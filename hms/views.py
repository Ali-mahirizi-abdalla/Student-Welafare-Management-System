from django.shortcuts import render, redirect, get_object_or_404
# Trigger reload
from django.conf import settings
from django.core.paginator import Paginator
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import (Student, Meal, Activity, AwayPeriod, Announcement, Document, MaintenanceRequest,
                     Message, AuditLog,
                     LeaveRequest, DefermentRequest, Visitor, EmergencyAlert,
                     Room, RoomAssignment, RoomChangeRequest, Payment, Notification, LoginActivity, LostItem, StaffProfile, StaffInvitation,
                     AdminSubscription, RegistrationPayment, TutoringPost, HealthAppointment)
from .decorators import (
    role_required, permission_required, staff_only, admin_only,
    super_admin_required, welfare_officer_required,
    hostel_manager_required, kitchen_manager_required, security_required
)
from .utils.telegram import send_telegram_message

# ==================== Authentication ====================
from .forms import (
    StudentRegistrationForm, StaffRegistrationForm, ProfileEditForm, AwayModeForm, ActivityForm, DocumentForm, 
    TimetableForm, RoomSelectionForm, MessageForm, MaintenanceRequestForm,
    MaintenanceStatusForm, RoomForm, RoomAssignmentForm, RoomChangeRequestForm,
    LeaveRequestForm, DefermentRequestForm, LeaveApprovalForm, VisitorForm, AnnouncementForm, LostItemForm,
    HealthAppointmentForm, HealthStaffUpdateForm
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
ROLE_BANNERS = {
    'super_admin': {
        'icon': '👑', 'name': 'Super Administrator',
        'description': 'Full system access – all modules and features',
        'restriction': 'FULL ACCESS: No restrictions', 'badge_color': 'navy'
    },
    'vice_chancellor': {
        'icon': '👑', 'name': 'Vice Chancellor',
        'description': 'Executive oversight of all university operations',
        'restriction': 'FULL ACCESS: Restricted (No DB/Control Access)', 'badge_color': 'amber'
    },
    'deputy_vice_chancellor': {
        'icon': '📚', 'name': 'Deputy Vice Chancellor',
        'description': 'Deputy executive oversight and administration',
        'restriction': 'FULL ACCESS: Restricted (No DB/Control Access)', 'badge_color': 'amber'
    },
    'register_admin': {
        'icon': '📋', 'name': 'Register Admin',
        'description': 'Manage staff registrations and student enrollment',
        'restriction': 'ACCESS RESTRICTED: Registration Only', 'badge_color': 'purple'
    },
    'register_user': {
        'icon': '👤', 'name': 'Register User',
        'description': 'View all staff members (read-only)',
        'restriction': 'ACCESS RESTRICTED: Read-Only Staff View', 'badge_color': 'gray'
    },
    'dean_of_students': {
        'icon': '👨‍🎓', 'name': 'Dean of Students',
        'description': 'Manage student welfare, discipline, and affairs',
        'restriction': 'ACCESS RESTRICTED: Student Welfare Only', 'badge_color': 'teal'
    },
    'dean_graduate_school': {
        'icon': '🎓', 'name': 'Dean – Graduate School',
        'description': 'Manage Masters and PhD students only',
        'restriction': 'ACCESS RESTRICTED: Graduate Students Only', 'badge_color': 'teal'
    },
    'director_resource': {
        'icon': '💰', 'name': 'Director – Resource Mobilization',
        'description': 'Manage graduate school funding and grants',
        'restriction': 'ACCESS RESTRICTED: Graduate Funding Only', 'badge_color': 'green'
    },
    'director_tvet': {
        'icon': '🔧', 'name': 'Director – TVET',
        'description': 'Full TVET department management',
        'restriction': 'ACCESS RESTRICTED: TVET Department Only', 'badge_color': 'amber'
    },
    'deferment_officer': {
        'icon': '📋', 'name': 'Deferment Officer',
        'description': 'Process student deferment requests',
        'restriction': 'ACCESS RESTRICTED: Deferments Only', 'badge_color': 'purple'
    },
    'dept_mcs': {
        'icon': '💻', 'name': 'Dept MCS Coordinator',
        'description': 'Manage Computer Science department only',
        'restriction': 'ACCESS RESTRICTED: CS Department Only', 'badge_color': 'teal'
    },
    'health_manager': {
        'icon': '🏥', 'name': 'Health Manager',
        'description': 'Manage health services and patient records',
        'restriction': 'ACCESS RESTRICTED: Health Records Only', 'badge_color': 'green'
    },
    'maintenance_sup': {
        'icon': '🔧', 'name': 'Maintenance Supervisor',
        'description': 'Manage maintenance requests and technicians',
        'restriction': 'ACCESS RESTRICTED: Maintenance Only', 'badge_color': 'amber'
    },
    'warden': {
        'icon': '🏠', 'name': 'Warden',
        'description': 'Manage accommodation and room allocation',
        'restriction': 'ACCESS RESTRICTED: Accommodation Only', 'badge_color': 'purple'
    },
    'finance_officer': {
        'icon': '💰', 'name': 'Finance Officer',
        'description': 'Manage payments and M-Pesa records',
        'restriction': 'ACCESS RESTRICTED: Financial Data Only', 'badge_color': 'teal'
    },
    'security_officer': {
        'icon': '👤', 'name': 'Security Officer',
        'description': 'Manage visitors and entry/exit logs',
        'restriction': 'ACCESS RESTRICTED: Visitor Logs Only', 'badge_color': 'gray'
    },
    'news_editor': {
        'icon': '📢', 'name': 'News Editor',
        'description': 'Create and publish news and alerts',
        'restriction': 'ACCESS RESTRICTED: News & Alerts Only', 'badge_color': 'teal'
    },
    'news_auditor': {
        'icon': '📜', 'name': 'News Auditor',
        'description': 'Read-only news audit logs',
        'restriction': 'READ-ONLY ACCESS: Cannot modify news', 'badge_color': 'gray'
    },
    'emergency_coord': {
        'icon': '🚨', 'name': 'Emergency Coordinator',
        'description': 'Send emergency alerts',
        'restriction': 'ACCESS RESTRICTED: Emergency Alerts Only', 'badge_color': 'navy'
    },
    'support_agent': {
        'icon': '💬', 'name': 'Support Agent',
        'description': 'Manage student chats and tickets',
        'restriction': 'ACCESS RESTRICTED: Student Support Only', 'badge_color': 'teal'
    },
    'auditor': {
        'icon': '📜', 'name': 'Auditor',
        'description': 'Read-only system audit logs',
        'restriction': 'READ-ONLY ACCESS: Cannot modify data', 'badge_color': 'gray'
    },
    'diploma_coordinator': {
        'icon': '🎓', 'name': 'Diploma Coordinator (TVET)',
        'description': 'Limited to Diploma Student Management',
        'restriction': 'ACCESS RESTRICTED: DIPLOMA STUDENTS ONLY', 'badge_color': 'amber'
    },
    'dept_coordinator': {
        'icon': '🏫', 'name': 'Department Coordinator',
        'description': 'Manage own department students only',
        'restriction': 'ACCESS RESTRICTED: Department Only', 'badge_color': 'teal'
    }
}
# ==================== Authentication ====================
def register_student(request):
    """
    Handle student registration logic.
    Students are now registered directly without mandatory payment.
    """
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    student = form.save()
                    # Create default notification preferences
                    from .models import NotificationPreference
                    NotificationPreference.objects.get_or_create(user=student.user)
                login(request, student.user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, "Registration successful! Welcome to Campus Care.")
                # Fire welcome SMS (only if student opted in via preferences later)
                try:
                    from .notifications import notify_welcome
                    notify_welcome(student)
                except Exception:
                    pass
                return redirect('hms:student_dashboard')
            except Exception as e:
                messages.error(request, f"Registration failed: {str(e)}")
        else:
            for field, errors in form.errors.items():
                messages.error(request, f"{field}: {', '.join(errors)}")
    else:
        form = StudentRegistrationForm()
    return render(request, 'hms/register.html', {'form': form})


def check_registration_status(request, checkout_id):
    """AJAX view to poll registration payment status"""
    payment = get_object_or_404(RegistrationPayment, checkout_request_id=checkout_id)
    if payment.status == 'Completed':
        # Create the user here once payment is confirmed
        if payment.temp_user_data:
            from .forms import StudentRegistrationForm
            # We recreate the form with the stored data
            form = StudentRegistrationForm(payment.temp_user_data)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        student = form.save()
                        payment.temp_user_data = None # Clear data after use
                        payment.save()
                    login(request, student.user, backend='django.contrib.auth.backends.ModelBackend')
                    return JsonResponse({'status': 'Success', 'redirect_url': reverse('hms:student_dashboard')})
                except Exception as e:
                    return JsonResponse({'status': 'Error', 'message': str(e)})
            else:
                return JsonResponse({'status': 'Error', 'message': 'Invalid form data in session'})
        else:
            # User already created?
            return JsonResponse({'status': 'Success', 'redirect_url': reverse('hms:student_dashboard')})
    elif payment.status == 'Failed':
        return JsonResponse({'status': 'Failed', 'message': 'Payment failed. Please try again.'})
    
    return JsonResponse({'status': 'Pending'})

@csrf_exempt
def mpesa_callback(request):
    """Handle STK Push callbacks from Safaricom"""
    try:
        data = json.loads(request.body)
        stk_callback = data.get('Body', {}).get('stkCallback', {})
        result_code = stk_callback.get('ResultCode')
        checkout_id = stk_callback.get('CheckoutRequestID')
        
        if result_code == 0:
            # Payment Success
            # Use metadata to get the transaction ID
            metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            transaction_id = next((item['Value'] for item in metadata if item['Name'] == 'MpesaReceiptNumber'), None)
            
            # Update RegistrationPayment
            reg_payment = RegistrationPayment.objects.filter(checkout_request_id=checkout_id).first()
            if reg_payment:
                reg_payment.status = 'Completed'
                reg_payment.transaction_id = transaction_id
                reg_payment.save()
            
            # Update AdminSubscription
            admin_sub = AdminSubscription.objects.filter(checkout_request_id=checkout_id).first()
            if admin_sub:
                admin_sub.status = 'Active'
                admin_sub.transaction_id = transaction_id
                admin_sub.last_payment_date = timezone.now()
                expiry_days = 365 if admin_sub.billing_cycle == 'annual' else 30
                admin_sub.expiry_date = timezone.now() + timedelta(days=expiry_days)
                admin_sub.save()
                # Clear system lock cache if implemented
                from django.core.cache import cache
                cache.delete('system_subscription_active')
        else:
            # Payment Failed
            reg_payment = RegistrationPayment.objects.filter(checkout_request_id=checkout_id).first()
            if reg_payment:
                reg_payment.status = 'Failed'
                reg_payment.save()
                
            admin_sub = AdminSubscription.objects.filter(checkout_request_id=checkout_id).first()
            if admin_sub:
                admin_sub.status = 'Failed'
                admin_sub.save()
                
    except Exception as e:
        print(f"Callback processing error: {e}")
        
    return HttpResponse("OK")


def register_staff(request):
    """
    Handle staff registration logic.
    For guests: via a valid invitation token.
    For admins: directly (original functionality).
    """
    invite_token = request.GET.get('invite') or request.POST.get('invite')
    invite = None
    if invite_token:
        invite = StaffInvitation.objects.filter(token=invite_token).first()
        if not invite or not invite.is_valid():
            messages.error(request, "Invalid or expired invitation link.")
            return redirect('hms:login')
    
    # Require login and admin permission if not self-registering
    if not invite:
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path(), login_url='hms:login')
        if not request.user.is_superuser:
            staff_profile = getattr(request.user, 'staff_profile', None)
            if not staff_profile or staff_profile.role not in ['super_admin', 'vice_chancellor', 'deputy_vice_chancellor']:
                messages.error(request, "Access Denied: Only super admins can register staff.")
                return redirect('hms:admin_dashboard')

    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    staff = form.save()
                    if invite:
                        if invite.role != 'ANY':
                            staff.role = invite.role  # Secure role assignment
                        staff.is_approved = False
                        staff.save()
                        invite.used_count += 1
                        invite.save()
                        messages.success(request, f"Registration successful! Your account as {staff.get_role_display()} is pending approval by the Super Admin.")
                        return redirect('hms:login')
                    else:
                        messages.success(request, f"Staff member {staff.user.get_full_name()} registered successfully!")
                        return redirect('hms:admin_dashboard')
            except Exception as e:
                messages.error(request, f"Error creating staff: {str(e)}")
        else:
            for field, errors in form.errors.items():
                messages.error(request, f"{field}: {', '.join(errors)}")
    else:
        # Pre-populate role if invite exists
        initial_role = invite.role if invite else None
        form = StaffRegistrationForm(initial_role=initial_role)

    base_template = 'hms/auth_base.html' if invite else 'hms/base.html'
    return render(request, 'hms/admin/register_staff.html', {
        'form': form,
        'role_choices': StaffProfile.ROLE_CHOICES,
        'token': invite_token,
        'invite': invite,
        'base_template': base_template,
    })


@csrf_exempt
def user_login(request):
    """Login view for all users with role selection"""
    if request.user.is_authenticated:
        staff_profile = getattr(request.user, 'staff_profile', None)
        if staff_profile and not staff_profile.is_approved:
            logout(request)
            messages.error(request, 'Your account is pending approval by the Super Admin. Please contact the administrator.')
            return redirect('hms:login')

        if hasattr(request.user, 'staff_profile') or request.user.is_superuser or request.user.is_staff:
            return redirect('hms:dashboard_redirect')
        elif hasattr(request.user, 'student_profile'):
            return redirect('hms:student_dashboard')
        else:
            return redirect('hms:dashboard_redirect')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Check if staff profile is approved
            staff_profile = getattr(user, 'staff_profile', None)
            if staff_profile and not staff_profile.is_approved:
                messages.error(request, 'Your account is pending approval by the Super Admin. Please contact the administrator.')
                return render(request, 'hms/login.html', {'form': form})

            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            
            if hasattr(user, 'staff_profile') or user.is_superuser or user.is_staff:
                return redirect('hms:dashboard_redirect')
            elif hasattr(user, 'student_profile'):
                return redirect('hms:student_dashboard')
            else:
                return redirect('hms:dashboard_redirect')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'hms/login.html', {'form': form})

@login_required
@csrf_exempt
def user_logout(request):
    """Accept both GET and POST to avoid CSRF errors from link-based logouts."""
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

@login_required
def dashboard_redirect(request):
    """Unified redirect for staff dashboards based on role"""
    if request.user.is_superuser:
        return redirect('hms:admin_dashboard')

    if not hasattr(request.user, 'staff_profile'):
        if request.user.is_staff:
            return redirect('hms:admin_dashboard')
        return redirect('hms:student_dashboard')

    role = getattr(request.user.staff_profile, 'role', None)

    # 23 Role Dashboard Redirection router
    if role == 'super_admin':
        return redirect('hms:admin_dashboard')
    elif role == 'vice_chancellor':
        return redirect('hms:admin_dashboard')
    elif role == 'deputy_vice_chancellor':
        return redirect('hms:admin_dashboard')
    elif role == 'register_admin':
        return redirect('hms:reg_admin_dashboard')
    elif role == 'register_user':
        return redirect('hms:reg_user_dashboard')
    elif role == 'dean_of_students':
        return redirect('hms:admin_dashboard') # Fallback to admin_dashboard
    elif role == 'dean_graduate_school':
        return redirect('hms:dean_grad_dashboard')
    elif role == 'director_resource':
        return redirect('hms:dir_resource_dashboard')
    elif role == 'director_tvet':
        return redirect('hms:director_tvet_dashboard')
    elif role == 'deferment_officer':
        return redirect('hms:deferment_officer_dashboard')
    elif role == 'dept_mcs':
        return redirect('hms:dept_mcs_dashboard')
    elif role == 'health_manager':
        return redirect('hms:health_manager_dashboard')
    elif role == 'maintenance_sup':
        return redirect('hms:maintenance_supervisor_dashboard')
    elif role == 'warden':
        return redirect('hms:admin_dashboard') # Fallback to admin_dashboard
    elif role == 'finance_officer':
        return redirect('hms:finance_officer_dashboard')
    elif role == 'security_officer':
        return redirect('hms:admin_dashboard') # Fallback to admin_dashboard
    elif role == 'news_editor':
        return redirect('hms:news_editor_dashboard')
    elif role == 'news_auditor':
        return redirect('hms:news_auditor_dashboard')
    elif role == 'emergency_coord':
        return redirect('hms:emergency_coordinator_dashboard')
    elif role == 'support_agent':
        return redirect('hms:support_agent_dashboard')
    elif role == 'auditor':
        return redirect('hms:auditor_dashboard')
    elif role == 'diploma_coordinator':
        return redirect('hms:diploma_coordinator_dashboard')
    elif role == 'dept_coordinator':
        return redirect('hms:dept_coordinator_dashboard')
    elif role == 'librarian':
        return redirect('library:librarian_dashboard')
    elif role == 'counsellor':
        return redirect('hms:counsellor_dashboard')

    return redirect('hms:admin_dashboard')



@login_required
def director_tvet_dashboard(request):
    # Ensure user has correct role
    if not hasattr(request.user, 'staff_profile') or request.user.staff_profile.role != 'director_tvet':
        return redirect('hms:dashboard_redirect')
        
    students = Student.objects.filter(level_of_study='diploma')
    context = {
        'user': request.user,
        'students_count': students.count(),
        'graduating_count': students.filter(is_graduating=True).count(),
        'attachment_count': students.filter(is_on_attachment=True).count(),
    }
    return render(request, 'hms/tvet/dashboard_tvet.html', context)

@login_required
def diploma_coordinator_dashboard(request):
    if not hasattr(request.user, 'staff_profile') or request.user.staff_profile.role != 'diploma_coordinator':
        return redirect('hms:dashboard_redirect')
        
    students = Student.objects.filter(level_of_study='diploma', assigned_coordinator=request.user)
    context = {
        'user': request.user,
        'students_count': students.count(),
        'graduating_count': students.filter(is_graduating=True).count(),
        'attachment_count': students.filter(is_on_attachment=True).count(),
    }
    return render(request, 'hms/diploma/dashboard_diploma.html', context)


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
    # Guard: redirect staff/admin users away from student dashboard
    if hasattr(request.user, 'staff_profile') or request.user.is_superuser or request.user.is_staff:
        return redirect('hms:dashboard_redirect')

    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        # Auto-create profile for genuine students only
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

    # === QUICK STATS CALCULATIONS ===
    # 1. Meals This Week
    week_ago = today - timedelta(days=7)
    meals_this_week = Meal.objects.filter(
        student=student,
        date__gte=week_ago,
        date__lte=today
    ).aggregate(
        total=models.Count('id', filter=models.Q(breakfast=True) | models.Q(early=True) | models.Q(supper=True))
    )['total'] or 0
    
    # 2. Days in Hostel (from first meal date or profile creation)
    first_meal = Meal.objects.filter(student=student).order_by('date').first()
    if first_meal:
        days_in_hostel = (today - first_meal.date).days
    else:
        days_in_hostel = 0
    
    # 3. Upcoming Payments (mock data - no Payment model)
    upcoming_payments = {
        'count': 0,
        'amount': 0,
    }
    
    # 4. Active Requests (maintenance)
    from hms.models import MaintenanceRequest
    active_requests = MaintenanceRequest.objects.filter(
        student=student,
        status__in=['pending', 'in_progress']
    ).count()
    
    # === WEATHER DATA ===
    weather_data = {
        'temperature': 24,  # Mock data - Celsius
        'condition': 'Partly Cloudy',
        'icon': 'cloud',  # Options: sun, cloud, rain, storm
        'location': 'Campus',
    }
    # TODO: Integrate real weather API in production

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
        # Quick Stats
        'meals_this_week': meals_this_week,
        'days_in_hostel': days_in_hostel,
        'upcoming_payments': upcoming_payments,
        'active_requests': active_requests,
        'weather_data': weather_data,
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
        'recent_tutoring': TutoringPost.objects.filter(is_active=True).exclude(student=student).select_related('student__user')[:3],
        'tutoring_count': TutoringPost.objects.filter(is_active=True).count(),
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
    
    # Generate QR code for student ID
    import qrcode
    import io
    import base64
    
    qr_code_data = None
    if student.university_id:
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(student.university_id)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for embedding in template
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        qr_code_data = base64.b64encode(buffer.getvalue()).decode()
    
    # Payment summary (mock data - no Payment model exists yet)
    payment_summary = {
        'total_paid': 0,
        'amount_pending': 0,
        'next_due_date': None,
        'status': 'no_records',  # Options: 'paid', 'pending', 'overdue', 'no_records'
    }
    
    # Forms
    room_form = RoomSelectionForm(instance=student)
    timetable_form = TimetableForm(instance=student)

    context = {
        'student': student,
        'meal_history': meal_history,
        'room_form': room_form,
        'timetable_form': timetable_form,
        'profile_form': profile_form,
        'qr_code_data': qr_code_data,
        'payment_summary': payment_summary,
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
@role_required(allowed_roles=[
    # actual model keys
    'super_admin', 'vice_chancellor', 'deputy_vice_chancellor', 'register_admin',
    'register_user', 'dean_of_students', 'dean_graduate_school', 'director_resource',
    'director_tvet', 'deferment_officer', 'dept_mcs', 'health_manager',
    'maintenance_sup', 'warden', 'finance_officer', 'security_officer',
    'news_editor', 'news_auditor', 'emergency_coord', 'support_agent',
    'auditor', 'diploma_coordinator', 'dept_coordinator',
    # legacy names
    'Super Admin', 'Welfare Officer', 'Hostel Manager', 'Kitchen Manager', 'Security',
])
@login_required
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

    # Department counts for flash cards
    dept_counts = {
        'education': Student.objects.filter(program_of_study__icontains='Education').count(),
        'agriculture': Student.objects.filter(program_of_study__icontains='Agriculture').count(),
        'business': Student.objects.filter(program_of_study__icontains='Business').count(),
        'environmental': Student.objects.filter(program_of_study__icontains='Environmental').count(),
        'spas': Student.objects.filter(models.Q(program_of_study__icontains='SPAS') | models.Q(program_of_study__icontains='Spatial')).count(),
        'health': Student.objects.filter(program_of_study__icontains='Health').count(),
    }

    # Level of Study breakdown
    level_counts = {
        'diploma': Student.objects.filter(level_of_study='diploma').count(),
        'bachelors': Student.objects.filter(level_of_study='bachelors').count(),
        'masters': Student.objects.filter(level_of_study='masters').count(),
        'doctorate': Student.objects.filter(level_of_study='doctorate').count(),
        'postgrad_diploma': Student.objects.filter(level_of_study='postgrad_diploma').count(),
        'certificate': Student.objects.filter(level_of_study='certificate').count(),
    }
    level_percentages = {}
    if total_students > 0:
        for level, count in level_counts.items():
            level_percentages[level] = round((count / total_students) * 100, 1)
    else:
        for level in level_counts:
            level_percentages[level] = 0.0


    # Staff Role Detection
    staff_profile = getattr(request.user, 'staff_profile', None)
    staff_role = staff_profile.role if staff_profile else None
    staff_category = staff_profile.get_category() if staff_profile else None
    
    # Dining & Revenue Metrics
    total_meals_served_today = today_stats['breakfast'] + today_stats['early'] + today_stats['supper']
    total_revenue = Payment.objects.filter(status='Completed').aggregate(models.Sum('amount'))['amount__sum'] or 0
    pending_payments_count = Payment.objects.filter(status='Pending').count()
    
    meal_completion_rate = 0
    if student_on_meals > 0:
        # Assuming max 2 meals per student (Breakfast + Supper)
        potential_meals = student_on_meals * 2
        meal_completion_rate = round((total_meals_served_today / potential_meals) * 100, 1) if potential_meals > 0 else 0
    
    # Get the role banner for the logged-in user
    user_role = staff_role
    role_banner = ROLE_BANNERS.get(user_role, {
        'icon': '👤',
        'name': user_role.replace('_', ' ').title() if user_role else 'Staff',
        'description': 'No description available',
        'restriction': 'ACCESS RESTRICTED',
        'badge_color': 'gray'
    })

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
        'total_occupancy': in_hostel_count + off_campus_count,
        'activities': activities,
        'staff_role': staff_role,
        'staff_category': staff_category,
        'is_superadmin': request.user.is_superuser,
        'level_counts': level_counts,
        'level_percentages': level_percentages,
        'total_students_all': total_students,
        'dept_counts': dept_counts,
        'role_banner': role_banner,
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

    # 1b. Global Student Search (for "Full Info")
    searched_students = []
    if search_query:
        searched_students = Student.objects.filter(
            models.Q(user__first_name__icontains=search_query) | 
            models.Q(user__last_name__icontains=search_query) |
            models.Q(university_id__icontains=search_query) |
            models.Q(phone__icontains=search_query)
        ).select_related('user').prefetch_related('room_assignments__room')[:5]

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
        'searched_students': searched_students,
        'staff_category_raw': staff_category,
    })

    return render(request, 'hms/admin/dashboard.html', context)

@login_required
@admin_only
def warden_dashboard(request):
    """Hostel / Warden Dashboard view"""
    return render(request, 'hms/dashboards/hostel_manager.html', {})

@login_required
@admin_only
def hostel_manager_dashboard(request):
    """Hostel Manager Dashboard view"""
    return render(request, 'hms/dashboards/hostel_manager.html', {})

@login_required
@admin_only
def welfare_officer_dashboard(request):
    return render(request, 'hms/dashboards/welfare_officer.html', {})

@login_required
@admin_only
def kitchen_manager_dashboard(request):
    return render(request, 'hms/dashboards/kitchen_manager.html', {})

@login_required
@admin_only
def security_dashboard(request):
    return render(request, 'hms/dashboards/security.html', {})

def render_role_dashboard(request, title, desc):
    today = date.today()
    context = {
        'dashboard_title': title,
        'dashboard_description': desc,
        'total_students': Student.objects.count(),
        'total_staff': StaffProfile.objects.count(),
        'pending_deferments': DefermentRequest.objects.filter(status='pending').count(),
        'pending_maintenance': MaintenanceRequest.objects.filter(status='pending').count(),
        'active_announcements': Announcement.objects.filter(is_active=True).count(),
        'recent_logs': AuditLog.objects.order_by('-timestamp')[:10],
        'recent_students': Student.objects.select_related('user').order_by('-created_at')[:5],
        'dept_counts': {
            'education': Student.objects.filter(program_of_study__icontains='Education').count(),
            'agriculture': Student.objects.filter(program_of_study__icontains='Agriculture').count(),
            'business': Student.objects.filter(program_of_study__icontains='Business').count(),
            'environmental': Student.objects.filter(program_of_study__icontains='Environmental').count(),
            'spas': Student.objects.filter(Q(program_of_study__icontains='SPAS') | Q(program_of_study__icontains='Spatial')).count(),
            'health': Student.objects.filter(program_of_study__icontains='Health').count(),
        }
    }
    return render(request, 'hms/rbac/role_dashboard.html', context)

@login_required
def vc_dashboard(request):
    return redirect('hms:admin_dashboard')

@login_required
def dvc_dashboard(request):
    return redirect('hms:admin_dashboard')

@login_required
def reg_admin_dashboard(request):
    if not hasattr(request.user, 'staff_profile') or request.user.staff_profile.role != 'register_admin':
        return redirect('hms:dashboard_redirect')
    context = {
        'dashboard_title': 'Registrar Admin Dashboard',
        'dashboard_description': 'Administrative oversight of all registered staff members.',
        'total_staff': StaffProfile.objects.count(),
        'active_staff_count': StaffProfile.objects.filter(is_approved=True).count(),
        'staff_list': StaffProfile.objects.all().select_related('user')[:50],
        'total_students': Student.objects.count(),
    }
    return render(request, 'hms/rbac/dashboards/executive_dashboard.html', context)

@login_required
def reg_user_dashboard(request):
    if not hasattr(request.user, 'staff_profile') or request.user.staff_profile.role != 'register_user':
        return redirect('hms:dashboard_redirect')
    context = {
        'dashboard_title': 'Registrar User Dashboard',
        'dashboard_description': 'View and manage registered staff records.',
        'total_staff': StaffProfile.objects.count(),
        'active_staff_count': StaffProfile.objects.filter(is_approved=True).count(),
        'staff_list': StaffProfile.objects.all().select_related('user')[:50],
        'total_students': Student.objects.count(),
    }
    return render(request, 'hms/rbac/dashboards/executive_dashboard.html', context)

@login_required
def dean_grad_dashboard(request):
    if not hasattr(request.user, 'staff_profile') or request.user.staff_profile.role != 'dean_graduate_school':
        return redirect('hms:dashboard_redirect')
    context = {
        'dashboard_title': 'Dean - Graduate School Dashboard',
        'dashboard_description': "Oversight of Master's and PhD students.",
        'masters_count': Student.objects.filter(level_of_study='masters').count(),
        'phd_count': Student.objects.filter(level_of_study='doctorate').count(),
        'masters_students': Student.objects.filter(level_of_study='masters').select_related('user'),
        'phd_students': Student.objects.filter(level_of_study='doctorate').select_related('user'),
    }
    return render(request, 'hms/rbac/dashboards/dean_grad_dashboard.html', context)

@login_required
def dir_resource_dashboard(request):
    if not hasattr(request.user, 'staff_profile') or request.user.staff_profile.role != 'director_resource':
        return redirect('hms:dashboard_redirect')
    context = {
        'dashboard_title': 'Director – Resource Mobilization',
        'dashboard_description': 'Manage university resources, grants, and donor relationships.',
        'grants': [
            {'title': 'Green Energy Initiative',    'agency': 'National Science Foundation', 'amount': '$0', 'status': 'review'},
            {'title': 'Rural Education Outreach',   'agency': 'Global Education Fund',       'amount': '$0', 'status': 'approved'},
            {'title': 'AI in Healthcare Research',  'agency': 'Tech Innovations Corp',       'amount': '$0', 'status': 'review'},
            {'title': 'Water Conservation Project', 'agency': 'UNESCO',                      'amount': '$0', 'status': 'pending'},
            {'title': 'Digital Literacy Program',   'agency': 'World Bank',                  'amount': '$0', 'status': 'pending'},
        ],
        'total_grants': '$0',
        'active_donors': 0,
        'pending_applications': 0,
        'ytd_utilization': '0%',
        'ytd_performance': '0% vs Last Year',
        'active_partners': 0,
    }
    return render(request, 'hms/resource_mobilization/dashboard_resource_mobilization.html', context)

@login_required
def news_auditor_dashboard(request):
    if not hasattr(request.user, 'staff_profile') or request.user.staff_profile.role != 'news_auditor':
        return redirect('hms:dashboard_redirect')
    context = {
        'dashboard_title': 'News Auditor Dashboard',
        'dashboard_description': 'Read-only audit log of all university news and announcements.',
        'total_news': Announcement.objects.count(),
        'announcements': Announcement.objects.all().order_by('-created_at')[:50],
    }
    return render(request, 'hms/rbac/dashboards/news_auditor_dashboard.html', context)

@login_required
def deferment_officer_dashboard(request):
    if not hasattr(request.user, 'staff_profile') or request.user.staff_profile.role != 'deferment_officer':
        return redirect('hms:dashboard_redirect')
    context = {
        'dashboard_title': 'Deferment Officer Dashboard',
        'dashboard_description': 'Process student deferment requests.',
        'pending_deferments': DefermentRequest.objects.filter(status='pending').select_related('student__user').order_by('-created_at'),
        'under_review_count': DefermentRequest.objects.filter(status='under_review').count(),
        'approved_count': DefermentRequest.objects.filter(status='approved').count(),
        'rejected_count': DefermentRequest.objects.filter(status='rejected').count(),
    }
    return render(request, 'hms/rbac/dashboards/deferment_officer_dashboard.html', context)

@login_required
def dept_mcs_dashboard(request):
    if not hasattr(request.user, 'staff_profile') or request.user.staff_profile.role != 'dept_mcs':
        return redirect('hms:dashboard_redirect')
    # Filter CS Students
    students = Student.objects.filter(program_of_study__icontains='Computer Science').select_related('user')
    context = {
        'dashboard_title': 'MCS Coordinator Dashboard',
        'dashboard_description': 'Manage Computer Science department students and courses.',
        'students_count': students.count(),
        'students_list': students[:50],
    }
    return render(request, 'hms/rbac/dashboards/dept_mcs_dashboard.html', context)

@login_required
def dept_coordinator_dashboard(request):
    if not hasattr(request.user, 'staff_profile') or request.user.staff_profile.role != 'dept_coordinator':
        return redirect('hms:dashboard_redirect')
    context = {
        'dashboard_title': 'Department Coordinator Dashboard',
        'dashboard_description': 'Manage your department students, courses and reports.',
        'students_count': Student.objects.count(),
        'students_list': Student.objects.all().select_related('user')[:50],
    }
    return render(request, 'hms/rbac/dashboards/dept_coordinator_dashboard.html', context)

@login_required
def health_manager_dashboard(request):
    if not hasattr(request.user, 'staff_profile') or request.user.staff_profile.role != 'health_manager':
        return redirect('hms:dashboard_redirect')
    return redirect('hms:manage_health')

@login_required
def maintenance_supervisor_dashboard(request):
    if not hasattr(request.user, 'staff_profile') or request.user.staff_profile.role != 'maintenance_sup':
        return redirect('hms:dashboard_redirect')
    return redirect('hms:manage_maintenance')

@login_required
def finance_officer_dashboard(request):
    if not hasattr(request.user, 'staff_profile') or request.user.staff_profile.role != 'finance_officer':
        return redirect('hms:dashboard_redirect')
    return redirect('hms:manage_payments')

@login_required
def news_editor_dashboard(request):
    if not hasattr(request.user, 'staff_profile') or request.user.staff_profile.role != 'news_editor':
        return redirect('hms:dashboard_redirect')
    return redirect('hms:manage_announcements')

@login_required
def emergency_coordinator_dashboard(request):
    if not hasattr(request.user, 'staff_profile') or request.user.staff_profile.role != 'emergency_coord':
        return redirect('hms:dashboard_redirect')
    return redirect('hms:emergency_broadcast')

@login_required
def support_agent_dashboard(request):
    if not hasattr(request.user, 'staff_profile') or request.user.staff_profile.role != 'support_agent':
        return redirect('hms:dashboard_redirect')
    return redirect('hms:chat')

@login_required
def auditor_dashboard(request):
    if not hasattr(request.user, 'staff_profile') or request.user.staff_profile.role != 'auditor':
        return redirect('hms:dashboard_redirect')
    return redirect('hms:audit_logs')


@login_required
@admin_only
def tvet_director_dashboard(request):
    """TVET Director Dashboard view"""
    # Get the role banner for the logged-in user
    staff_profile = getattr(request.user, 'staff_profile', None)
    user_role = staff_profile.role if staff_profile else None
    role_banner = ROLE_BANNERS.get(user_role, {
        'icon': '👤',
        'name': user_role.replace('_', ' ').title() if user_role else 'Staff',
        'description': 'No description available',
        'restriction': 'ACCESS RESTRICTED',
        'badge_color': 'gray'
    })

    context = {
        'dashboard_title': 'Director - TVET Dashboard',
        'dashboard_description': 'Oversight of TVET students, staff, and industrial attachments.',
        'tvet_students_count': Student.objects.filter(level_of_study='diploma').count(),
        'tvet_staff_count': 28,
        'mock_attachments': [
            {'student': 'John Doe', 'course': 'Diploma in Engineering Tech', 'company': 'Toyota Manufacturing', 'supervisor': 'H. Tanaka', 'status': 'Active'},
            {'student': 'Jane Smith', 'course': 'Diploma in Hospitality', 'company': 'Grand Horizon Hotel', 'supervisor': 'M. Roux', 'status': 'Active'},
            {'student': 'Sam Wilson', 'course': 'Diploma in IT Support', 'company': 'TechServe Solutions', 'supervisor': 'P. Patel', 'status': 'Completed'},
            {'student': 'Emily Davis', 'course': 'Diploma in Business Admin', 'company': 'Global Finance Corp', 'supervisor': 'A. Johnson', 'status': 'Pending'},
        ],
        'role_banner': role_banner,
    }
    return render(request, 'hms/rbac/dashboards/dir_tvet_dashboard.html', context)

@login_required
@role_required([
    # actual model keys
    'super_admin', 'vice_chancellor', 'deputy_vice_chancellor', 'register_admin',
    'register_user', 'dean_of_students', 'dean_graduate_school', 'director_resource',
    'director_tvet', 'deferment_officer', 'dept_mcs', 'health_manager',
    'maintenance_sup', 'warden', 'finance_officer', 'security_officer',
    'news_editor', 'news_auditor', 'emergency_coord', 'support_agent',
    'auditor', 'diploma_coordinator', 'dept_coordinator',
    # legacy
    'Admin', 'Warden', 'Finance', 'DEFERMENT', 'MAINTENANCE_HOSTEL', 'ACTIVITIES_ROOMS', 'NEWS_ALERT', 'VISITORS', 'AUDIT_LOGS'
])
@login_required
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
@role_required([
    # actual model keys
    'super_admin', 'vice_chancellor', 'deputy_vice_chancellor', 'register_admin',
    'register_user', 'dean_of_students', 'dean_graduate_school', 'director_resource',
    'director_tvet', 'deferment_officer', 'dept_mcs', 'health_manager',
    'maintenance_sup', 'warden', 'finance_officer', 'security_officer',
    'news_editor', 'news_auditor', 'emergency_coord', 'support_agent',
    'auditor', 'diploma_coordinator', 'dept_coordinator',
    # legacy
    'Admin', 'Warden', 'Finance', 'DEFERMENT', 'MAINTENANCE_HOSTEL', 'ACTIVITIES_ROOMS', 'NEWS_ALERT', 'VISITORS', 'AUDIT_LOGS'
])
@login_required
def export_students_csv(request):
    """Export comprehensive student data to CSV including all details"""
    
    import csv
    from datetime import date
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="SWMS_Student_Welfare_Report_{date.today()}.csv"'
    
    writer = csv.writer(response)
    
    # Comprehensive header
    writer.writerow([
        'Full Name', 'University ID', 'Email', 'Phone', 'Gender', 'County',
        'Residence Type', 'Hostel', 'Room Number', 'Program of Study',
        'Disability', 'Is Warden', 'Is On Attachment', 'Is Graduating',
        'Active Deferments', 'Deferment Types', 'Deferment Status',
        'Pending Maintenance Requests', 'Completed Maintenance Requests',
        'Total Payments', 'Pending Payments', 'Completed Payments',
        'Active Visitors Today', 'Emergency Alerts Count',
        'Created At'
    ])
    
    students = Student.objects.all().select_related('user').prefetch_related(
        'deferment_requests', 'maintenance_requests', 'payments', 'visitors', 'emergency_alerts'
    )
    
    for student in students:
        # Deferment info
        deferments = student.deferment_requests.all()
        active_deferments = deferments.filter(status='approved').count()
        deferment_types = ', '.join(set([d.get_deferment_type_display() for d in deferments]))
        deferment_statuses = ', '.join(set([d.status for d in deferments]))
        
        # Maintenance info
        maintenance = student.maintenance_requests.all()
        pending_maintenance = maintenance.filter(status='pending').count()
        completed_maintenance = maintenance.filter(status='completed').count()
        
        # Payment info
        payments = student.payments.all()
        total_payments = payments.count()
        pending_payments = payments.filter(status='Pending').count()
        completed_payments = payments.filter(status='Completed').count()
        
        # Visitor info (today)
        active_visitors = student.visitors.filter(is_active=True).count()
        
        # Emergency alerts
        emergency_count = student.emergency_alerts.count()
        
        writer.writerow([
            student.user.get_full_name(),
            student.university_id,
            student.user.email,
            student.phone,
            student.get_gender_display() if student.gender else '-',


            student.get_residence_type_display(),
            student.hostel or '-',
            student.room_number or '-',
            student.program_of_study or '-',
            student.get_disability_display(),
            'Yes' if student.is_warden else 'No',
            'Yes' if student.is_on_attachment else 'No',
            'Yes' if student.is_graduating else 'No',
            active_deferments,
            deferment_types or '-',
            deferment_statuses or '-',
            pending_maintenance,
            completed_maintenance,
            total_payments,
            pending_payments,
            completed_payments,
            active_visitors,
            emergency_count,
            student.created_at.strftime('%Y-%m-%d') if student.created_at else '-'
        ])
        
    return response


@login_required
@permission_required('view_payments')
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
@role_required(allowed_roles=['super_admin', 'dean_of_students', 'register_admin', 'Super Admin', 'Welfare Officer'])
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
        messages.success(request, 'âœ… All students have confirmed their meals for tomorrow!')
        return redirect('hms:admin_dashboard')
    
    # Prepare email content
    unconfirmed_count = unconfirmed_students.count()
    student_list = '\n'.join([
        f"  â€¢ {student.user.get_full_name()} ({student.university_id}) - {student.user.email}"
        for student in unconfirmed_students
    ])
    
    subject = f'âš ï¸ Meal Confirmation Alert - {unconfirmed_count} Students Unconfirmed for {tomorrow.strftime("%B %d, %Y")}'
    
    message = f"""
Hello Admin,

This is an automated notification from the Student Welfare Management System.

ðŸ“… Date: {tomorrow.strftime("%A, %B %d, %Y")}
âš ï¸ Unconfirmed Students: {unconfirmed_count} out of {all_students.count()}

The following students have NOT confirmed their meals for tomorrow:

{student_list}

Please remind these students to confirm their meal preferences before the deadline.

---
ðŸ”— Access the admin dashboard: {request.build_absolute_uri('/kitchen/dashboard/')}

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
            f'âœ… Email notification sent successfully to {settings.ADMIN_EMAIL}! '
            f'{unconfirmed_count} unconfirmed students for {tomorrow.strftime("%B %d")}'
        )
        
    except Exception as e:
        messages.error(request, f'âŒ Failed to send email: {str(e)}')
    
    return redirect('hms:admin_dashboard')

@login_required
@role_required(allowed_roles=['super_admin', 'dean_of_students', 'register_admin', 'Super Admin', 'Welfare Officer'])
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
@role_required(['super_admin', 'warden', 'Admin', 'Warden'])
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
@role_required(['super_admin', 'warden', 'Admin', 'Warden'])
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


        'gender_choices': Student.GENDER_CHOICES,
        'disability_choices': Student.DISABILITY_CHOICES,
    }
    
    return render(request, 'hms/admin/edit_student.html', context)

@login_required
@require_POST
@role_required(['super_admin', 'Admin'])
def delete_student(request, user_id):
    """Delete student (admin only)"""
        
    user = get_object_or_404(User, id=user_id)
    student_name = user.get_full_name() or user.username
    user.delete()
    messages.success(request, f"Student '{student_name}' deleted successfully.")
    return redirect('hms:manage_students')

@login_required
@role_required(['super_admin', 'warden', 'Admin', 'Warden'])
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
@role_required(['super_admin', 'warden', 'Admin', 'Warden'])
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
@permission_required('view_news')
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
@role_required(['super_admin', 'register_admin', 'Admin'])
def delete_announcement(request, pk):
    """Delete an announcement (admin only)"""
        
    announcement = get_object_or_404(Announcement, pk=pk)
    announcement_title = announcement.title
    announcement.delete()
    messages.success(request, f"News Alert '{announcement_title}' deleted successfully.")
    return redirect('hms:manage_announcements')

@login_required
@role_required(['super_admin', 'warden', 'Admin', 'Warden'])
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
@role_required(['super_admin', 'warden', 'Admin', 'Warden'])
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
@role_required(allowed_roles=['super_admin', 'health_manager', 'Super Admin', 'Kitchen Manager'])
def activities_list(request):
    """View and manage all activities"""
    
    activities = Activity.objects.all().order_by('weekday', 'time')
    context = {
        'activities': activities
    }
    return render(request, 'hms/admin/activities.html', context)

@login_required
@role_required(allowed_roles=['super_admin', 'health_manager', 'Super Admin', 'Kitchen Manager'])
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
    
    return render(request, 'hms/admin/activity_form_v2.html', {'edit_mode': False})

@login_required
@role_required(allowed_roles=['super_admin', 'health_manager', 'Super Admin', 'Kitchen Manager'])
def edit_activity(request, pk):
    
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
    
    return render(request, 'hms/admin/activity_form_v2.html', {'activity': activity, 'edit_mode': True})

@login_required
@require_POST
@role_required(allowed_roles=['super_admin', 'health_manager', 'Super Admin', 'Kitchen Manager'])
def delete_activity(request, pk):
    
    activity = get_object_or_404(Activity, pk=pk)
    activity_name = activity.display_name
    activity.delete()
    messages.success(request, f"Activity '{activity_name}' deleted successfully!")
    return redirect('hms:activities')

@login_required
@role_required(allowed_roles=['super_admin', 'health_manager', 'Super Admin', 'Kitchen Manager'])
def toggle_activity_status(request, pk):
    
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
@role_required(['super_admin', 'warden', 'Admin', 'Warden'])
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
@permission_required('view_maintenance')
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
@role_required(['super_admin', 'warden', 'maintenance_sup', 'Admin', 'Warden', 'MAINTENANCE_HOSTEL', 'ACTIVITIES_ROOMS'])
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
@role_required(allowed_roles=['super_admin', 'warden', 'Super Admin', 'Hostel Manager'])
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
@role_required(['super_admin', 'register_admin', 'Admin'])
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
@role_required(['super_admin', 'register_admin', 'Admin'])
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
@permission_required('view_accommodation')
def delete_room(request, pk):
    """Delete a room (admin only)"""
    
    room = get_object_or_404(Room, pk=pk)
    room_number = room.room_number
    room.delete()
    messages.success(request, f'Room {room_number} deleted successfully!')
    return redirect('hms:room_list')


@login_required
@permission_required('view_accommodation')
def room_assignments(request):
    """View all room assignments (admin only)"""
    
    assignments = RoomAssignment.objects.filter(is_active=True).select_related('student__user', 'room')
    
    context = {
        'assignments': assignments,
        'total_assigned': assignments.count(),
    }
    
    return render(request, 'hms/admin/room_assignments.html', context)


@login_required
@permission_required('view_accommodation')
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
@permission_required('view_accommodation')
def room_change_requests(request):
    """View all room change requests (admin only)"""
    
    requests_list = RoomChangeRequest.objects.all().select_related('student__user', 'current_room', 'requested_room')
    
    context = {
        'change_requests': requests_list,
        'pending_count': requests_list.filter(status='pending').count(),
    }
    
    return render(request, 'hms/admin/room_change_requests.html', context)


@login_required
@permission_required('view_accommodation')
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
@permission_required('view_reports')
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
@permission_required('view_reports')
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
@permission_required('view_reports')
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
@permission_required('view_reports')
def admin_deferment_approved(request):
    """Admin views approved deferment requests"""
    
    deferments = DefermentRequest.objects.filter(status='approved').select_related('student__user').order_by('-created_at')
    
    context = {
        'deferments': deferments,
        'title': 'Approved Deferments',
        'active_tab': 'approved'
    }
    return render(request, 'hms/admin/deferment_list.html', context)

@login_required
@permission_required('view_reports')
def admin_deferment_rejected(request):
    """Admin views rejected deferment requests"""
    
    deferments = DefermentRequest.objects.filter(status='rejected').select_related('student__user').order_by('-created_at')
    
    context = {
        'deferments': deferments,
        'title': 'Rejected Applications',
        'active_tab': 'rejected'
    }
    return render(request, 'hms/admin/deferment_list.html', context)

@login_required
@permission_required('view_reports')
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
@permission_required('view_reports')
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
@permission_required('view_reports')
def analytics_dashboard(request):
    """Comprehensive analytics dashboard for admins"""
    
    import json
    from django.db.models import Count, Q
    from django.db.models.functions import TruncDate
    
    today = date.today()
    # Rolling 7-day window (Today - 6 days)
    week_start = today - timedelta(days=6)
    # Rolling 30-day window (Today - 29 days)
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

    # Weekly Trends (Rolling 7 days)
    weekly_labels = [(week_start + timedelta(days=i)).strftime('%a') for i in range(7)]
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
@permission_required('view_emergency')
def emergency_broadcast(request):
    """View for sending emergency broadcasts via Telegram"""
    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        alert_level = request.POST.get('alert_level', 'INFO')
        
        if not message:
            messages.error(request, "Message cannot be empty.")
            return redirect('hms:emergency_broadcast')

        formatted_message = f"ðŸš¨ *{alert_level} ALERT* ðŸš¨\n\n{message}"
        success, response_msg = send_telegram_message(formatted_message)
        
        if success:
            messages.success(request, response_msg)
        else:
            messages.error(request, f"Failed to send broadcast: {response_msg}")
        
        return redirect('hms:emergency_broadcast')

    return render(request, 'hms/admin/emergency_broadcast.html')


@login_required
@permission_required('view_visitors')
def visitor_management(request):
    """View to list active visitors and check them in/out"""
    # Decorator handles permission
    
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
@permission_required('view_visitors')
def checkout_visitor(request, visitor_id):
    """View to check out a visitor"""
    
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
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('hms:dashboard_redirect')

    # Get active room assignment to find the fee
    room_assignment = RoomAssignment.objects.filter(student=student, is_active=True).first()
    default_amount = 0
    if room_assignment:
        default_amount = room_assignment.room.price_per_semester

    if request.method == 'POST':
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')
        
        # Basic validation
        if not phone or not amount:
            messages.error(request, "Please provide phone number and amount")
            return redirect('hms:pay_accommodation')

        payment = Payment.objects.create(
            student=student,
            amount=amount,
            phone_number=phone,
            status='Pending'
        )
        
        # Initiate STK Push
        mpesa = MpesaClient()
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
        
    return render(request, 'hms/student/pay_accommodation.html', {
        'default_amount': default_amount,
        'room_assignment': room_assignment
    })

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
@permission_required('view_audit')
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
@permission_required('view_audit')
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
@permission_required('view_reports')
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

# ==================== SUBSCRIPTION & LOCK ====================

@login_required
@admin_only
def admin_subscription_pay(request):
    """Admin page to initiate subscription payment"""
    # Get current subscription status
    subscription = AdminSubscription.objects.order_by('-created_at').first()
    
    if request.method == 'POST':
        plan = request.POST.get('plan', 'pro').lower()
        billing_cycle = request.POST.get('billing_cycle', 'monthly').lower()
        
        try:
            student_count = int(request.POST.get('student_count', 1000))
        except ValueError:
            student_count = 1000
            
        method = request.POST.get('method', 'mpesa').lower()
        
        # Calculate dynamic price on backend
        prices = {
            'basic': {'monthly': 3000, 'annual': 30000},
            'standard': {'monthly': 6000, 'annual': 60000},
            'pro': {'monthly': 10000, 'annual': 100000},
            'enterprise': {'monthly': 15000, 'annual': 150000},
        }
        
        plan_prices = prices.get(plan, prices['pro'])
        base_price = plan_prices.get(billing_cycle, plan_prices['monthly'])
        
        if student_count <= 250:
            multiplier = 0.8
        elif student_count <= 500:
            multiplier = 0.9
        elif student_count <= 2000:
            multiplier = 1.0
        elif student_count <= 5000:
            multiplier = 1.2
        else:
            multiplier = 1.5
            
        amount = int(round(base_price * multiplier))
        
        if method == 'card':
            # Card payment simulation: immediately activate
            expiry_days = 365 if billing_cycle == 'annual' else 30
            expiry_date = timezone.now() + timedelta(days=expiry_days)
            
            AdminSubscription.objects.create(
                plan=plan,
                billing_cycle=billing_cycle,
                student_count=student_count,
                amount=amount,
                status='Active',
                last_payment_date=timezone.now(),
                expiry_date=expiry_date,
                transaction_id=f"CARD-{int(timezone.now().timestamp())}",
                phone_number="Card Payment"
            )
            
            # Clear lock cache
            from django.core.cache import cache
            cache.delete('system_subscription_active')
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'Success', 'message': 'Card payment successful!'})
                
            messages.success(request, f"Payment Successful! Your {plan.title()} plan has been activated.")
            return redirect('hms:dashboard_redirect')
            
        else: # mpesa
            phone = request.POST.get('phone')
            if not phone:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'Error', 'message': 'Phone number is required.'})
                messages.error(request, "Phone number is required.")
            else:
                try:
                    client = MpesaClient()
                    callback_url = request.build_absolute_uri(reverse('hms:mpesa_callback'))
                    response = client.stk_push(
                        phone_number=phone,
                        amount=amount,
                        reference='subscription',
                        callback_url=callback_url,
                        description=f"Admin {plan.title()} Subscription"
                    )
                    
                    if response.get('ResponseCode') == '0':
                        AdminSubscription.objects.create(
                            plan=plan,
                            billing_cycle=billing_cycle,
                            student_count=student_count,
                            phone_number=phone,
                            amount=amount,
                            checkout_request_id=response.get('CheckoutRequestID'),
                            status='Pending'
                        )
                        msg = "STK Push sent! Please check your phone to complete payment."
                        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                            return JsonResponse({'status': 'Success', 'message': msg})
                        messages.success(request, msg)
                    else:
                        err = f"M-Pesa Error: {response.get('ResponseDescription')}"
                        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                            return JsonResponse({'status': 'Error', 'message': err})
                        messages.error(request, err)
                except Exception as e:
                    err_msg = f"Payment failed: {str(e)}"
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'status': 'Error', 'message': err_msg})
                    messages.error(request, err_msg)
                    
        return redirect('hms:admin_subscription_pay')

@login_required
def system_locked(request):
    """View to display the system-wide lock notice"""
    return render(request, 'hms/system_locked.html')

@login_required
@admin_only
def manage_subscriptions(request):
    """Admin view to monitor all payments (registration and system)"""
    reg_payments = RegistrationPayment.objects.all().order_by('-created_at')
    admin_subs = AdminSubscription.objects.all().order_by('-created_at')
    
    # Filter by search query
    query = request.GET.get('q', '').strip()
    if query:
        reg_payments = reg_payments.filter(
            Q(phone_number__icontains=query) |
            Q(transaction_id__icontains=query)
        )
        
    # Stats
    total_revenue = sum(p.amount for p in reg_payments if p.status == 'Completed') + \
                    sum(s.amount for s in admin_subs if s.status == 'Active')
    
    context = {
        'reg_payments': reg_payments,
        'admin_subs': admin_subs,
        'total_revenue': total_revenue,
        'query': query,
    }
    return render(request, 'hms/admin/manage_subscriptions.html', context)

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

@login_required
@require_POST
def mark_notification_read(request, notif_id):
    """Mark a notification as read via AJAX"""
    from .models import Notification
    from django.http import JsonResponse
    try:
        notification = Notification.objects.get(id=notif_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)

@login_required
def notifications_list(request):
    """View all notifications for the current user"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark all as read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'hms/notifications.html', {
        'notifications': notifications
    })

@login_required
def tutoring_hub(request):

    """Browse and filter tutoring posts"""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return redirect('hms:student_dashboard')

    post_type = request.GET.get('type', 'all')
    search_query = request.GET.get('q', '')

    posts = TutoringPost.objects.filter(is_active=True).select_related('student__user')

    if post_type == 'offer':
        posts = posts.filter(post_type='offer')
    elif post_type == 'request':
        posts = posts.filter(post_type='request')

    if search_query:
        posts = posts.filter(
            Q(subject__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    context = {
        'posts': posts,
        'post_type': post_type,
        'search_query': search_query,
        'student': student,
    }
    return render(request, 'hms/student/tutoring_hub.html', context)

@login_required
@require_POST
def create_tutoring_post(request):
    """Create a new tutoring offer or request"""
    try:
        student = request.user.student_profile
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        post_type = request.POST.get('post_type')

        if subject and description and post_type:
            TutoringPost.objects.create(
                student=student,
                subject=subject,
                description=description,
                post_type=post_type
            )
            messages.success(request, "Your tutoring post has been published!")
        else:
            messages.error(request, "Please fill in all fields.")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
    
    return redirect('hms:tutoring_hub')

@login_required
@require_POST
def delete_tutoring_post(request, post_id):
    """Delete a student's own tutoring post"""
    post = get_object_or_404(TutoringPost, id=post_id, student__user=request.user)
    post.delete()
    messages.success(request, "Post removed successfully.")
    return redirect('hms:tutoring_hub')


# ==================== RBAC DASHBOARDS ====================

@login_required
@super_admin_required
def super_admin_dashboard(request):
    """Redirect Super Admin to the main admin dashboard"""
    return redirect('hms:admin_dashboard')


@login_required
@welfare_officer_required
def welfare_officer_dashboard(request):
    """Welfare and Deferment management dashboard"""
    context = {
        'pending_deferments': DefermentRequest.objects.filter(status='pending').select_related('student__user').order_by('-created_at'),
        'under_review_deferments': DefermentRequest.objects.filter(status='under_review').select_related('student__user').count(),
        'approved_deferments': DefermentRequest.objects.filter(status='approved').count(),
        'total_students': Student.objects.count(),
        'recent_announcements': Announcement.objects.filter(is_active=True).order_by('-created_at')[:5],
        'recent_students': Student.objects.select_related('user').order_by('-created_at')[:5],
    }
    return render(request, 'hms/rbac/welfare_officer_dashboard.html', context)


@login_required
@hostel_manager_required
def hostel_manager_dashboard(request):
    """Hostel and Room management dashboard"""
    context = {
        'total_rooms': Room.objects.count(),
        'available_rooms': Room.objects.filter(is_available=True).count(),
        'occupied_rooms': Room.objects.filter(is_available=False).count(),
        'pending_room_changes': RoomChangeRequest.objects.filter(status='pending').count(),
        'recent_assignments': RoomAssignment.objects.select_related('student__user', 'room').order_by('-assigned_date')[:10],
        'pending_maintenance': MaintenanceRequest.objects.filter(status='pending').select_related('student__user').order_by('-created_at')[:5],
        'total_assigned': RoomAssignment.objects.filter(is_current=True).count(),
    }
    return render(request, 'hms/rbac/hostel_manager_dashboard.html', context)


@login_required
@kitchen_manager_required
def kitchen_manager_dashboard(request):
    """Kitchen and Meal management dashboard"""
    today = date.today()
    tomorrow = today + timedelta(days=1)
    context = {
        'today': today,
        'breakfast_count': Meal.objects.filter(date=today, breakfast=True).count(),
        'supper_count': Meal.objects.filter(date=today, supper=True).count(),
        'early_count': Meal.objects.filter(date=today, early=True).count(),
        'away_count': Meal.objects.filter(date=today, away=True).count(),
        'tomorrow_breakfast': Meal.objects.filter(date=tomorrow, breakfast=True).count(),
        'tomorrow_supper': Meal.objects.filter(date=tomorrow, supper=True).count(),
        'today_menu': Activity.objects.filter(active=True, weekday=today.weekday()).first(),
        'activities': Activity.objects.filter(active=True),
        'total_students': Student.objects.count(),
    }
    return render(request, 'hms/rbac/kitchen_manager_dashboard.html', context)


@login_required
@security_required
def security_dashboard(request):
    """Visitor log and security management dashboard"""
    today = date.today()
    context = {
        'active_visitors': Visitor.objects.filter(check_out_time__isnull=True).select_related('student__user').order_by('-check_in_time'),
        'today_visitors_count': Visitor.objects.filter(check_in_time__date=today).count(),
        'checked_out_today': Visitor.objects.filter(check_out_time__date=today).count(),
        'recent_visitors': Visitor.objects.select_related('student__user').order_by('-check_in_time')[:10],
        'recent_alerts': EmergencyAlert.objects.order_by('-created_at')[:5],
    }
    return render(request, 'hms/rbac/security_dashboard.html', context)


@login_required
def access_denied(request, exception=None):
    """Custom 403 Access Denied page (redirects to safety)"""
    from django.contrib import messages
    from django.shortcuts import redirect
    messages.error(request, 'Access Denied. You do not have permission to view this page.')
    return redirect('hms:dashboard_redirect')

@login_required
def page_not_found(request, exception=None):
    """Custom 404 Page Not Found page"""
    return render(request, 'hms/404.html', status=404)


# ==================== Health Services ====================

@login_required
def book_health_appointment(request):
    """View for students to book health appointments"""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, "Student profile required to book appointments.")
        return redirect('hms:student_dashboard')

    if request.method == 'POST':
        form = HealthAppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.student = student
            appointment.save()
            
            # Create notification for Health Admin
            # Find a health admin or use a generic broadcast
            health_admins = User.objects.filter(staff_profile__role='HEALTH_ADMIN')
            for admin in health_admins:
                Notification.objects.create(
                    user=admin,
                    notification_type='system',
                    title='New Health Appointment',
                    message=f'New {appointment.get_service_type_display()} appointment requested by {student.user.get_full_name()}.',
                    link=reverse('hms:manage_health')
                )
            
            messages.success(request, "Appointment requested successfully! Our team will review it shortly.")
            return redirect('hms:student_health_appointments')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = HealthAppointmentForm()

    return render(request, 'hms/health/book_appointment.html', {'form': form})

@login_required
def health_appointment_list(request):
    """List appointments for students or staff"""
    is_staff = hasattr(request.user, 'staff_profile') and request.user.staff_profile.get_category() == 'HEALTH_SERVICES'
    
    if is_staff:
        appointments = HealthAppointment.objects.all()
    else:
        try:
            student = request.user.student_profile
            appointments = HealthAppointment.objects.filter(student=student)
        except Student.DoesNotExist:
            appointments = []

    return render(request, 'hms/health/appointment_list.html', {
        'appointments': appointments,
        'is_staff': is_staff
    })

@login_required
def health_appointment_detail(request, pk):
    """View and update health appointment details"""
    appointment = get_object_or_404(HealthAppointment, pk=pk)
    is_health_staff = hasattr(request.user, 'staff_profile') and request.user.staff_profile.get_category() == 'HEALTH_SERVICES'
    
    # Permission check: Own appointment or Health Staff
    if not is_health_staff and appointment.student.user != request.user:
        messages.error(request, "Access Denied.")
        return redirect('hms:home')

    if request.method == 'POST' and is_health_staff:
        form = HealthStaffUpdateForm(request.POST, instance=appointment)
        if form.is_valid():
            appointment = form.save()
            # Notify student of update
            Notification.objects.create(
                user=appointment.student.user,
                notification_type='system',
                title=f'Appointment Updated: {appointment.get_status_display()}',
                message=f'Your {appointment.get_service_type_display()} appointment has been updated to {appointment.status}.',
                link=reverse('hms:student_health_appointments')
            )
            messages.success(request, "Appointment details updated.")
            return redirect('hms:manage_health')
    
    form = HealthStaffUpdateForm(instance=appointment) if is_health_staff else None

    return render(request, 'hms/health/appointment_detail.html', {
        'appointment': appointment,
        'form': form,
        'is_health_staff': is_health_staff
    })

@login_required
@permission_required('view_health')
def manage_health(request):
    """Dashboard for health staff"""
    staff_profile = getattr(request.user, 'staff_profile', None)
    staff_role = staff_profile.role if staff_profile else None
    
    # Filter appointments based on role if needed, or show all for admin
    if staff_role in ['CAMPUS_DOCTOR', 'CAMPUS_COUNSELOR']:
        assigned_appointments = HealthAppointment.objects.filter(assigned_staff=request.user)
        pending_appointments = HealthAppointment.objects.filter(status='pending', service_type='general' if staff_role == 'CAMPUS_DOCTOR' else 'counseling')
    else:
        assigned_appointments = HealthAppointment.objects.none()
        pending_appointments = HealthAppointment.objects.filter(status='pending')

    today = date.today()
    all_appointments = HealthAppointment.objects.all()
    
    stats = {
        'pending': all_appointments.filter(status='pending').count(),
        'assigned_to_me': all_appointments.filter(assigned_staff=request.user, status='ongoing').count(),
        'completed_today': all_appointments.filter(status='completed', updated_at__date=today).count(),
        'total_all_time': all_appointments.count(),
    }

    return render(request, 'hms/health/manage_health.html', {
        'pending_appointments': pending_appointments,
        'my_appointments': assigned_appointments.filter(status='ongoing'),
        'all_appointments': all_appointments.order_by('-created_at')[:50],
        'stats': stats,
        'staff_role': staff_role
    })






# ==================== Staff Management ====================

@login_required
@admin_only
def manage_staff(request):
    """Unified Staff and Role Management Dashboard"""
    staff_members = StaffProfile.objects.select_related('user').all().order_by('-created_at')
    
    # Statistics
    total_staff = staff_members.count()
    active_staff = User.objects.filter(staff_profile__isnull=False, is_active=True).count()
    pending_staff = User.objects.filter(staff_profile__isnull=False, is_active=False).count()
    
    # Add colors to staff members for the UI
    for staff in staff_members:
        staff.role_color = get_role_color(staff.role)

    invitations = StaffInvitation.objects.all().order_by('-created_at')
    active_invites = sum(1 for i in invitations if i.is_valid())
    
    # Roles Data
    role_choices = StaffProfile.ROLE_CHOICES
    roles_with_counts = []
    for role_code, role_label in role_choices:
        count = StaffProfile.objects.filter(role=role_code).count()
        roles_with_counts.append({
            'code': role_code,
            'label': role_label,
            'count': count,
            'color': get_role_color(role_code)
        })

    context = {
        'staff_members': staff_members,
        'total_staff': total_staff,
        'active_count': active_staff,
        'pending_count': pending_staff,
        'invited_count': active_invites,
        'invitations': invitations,
        'roles': roles_with_counts,
        'role_choices': role_choices,
        'page_title': 'Staff & Role Management',
    }
    
    return render(request, 'hms/rbac/manage_roles.html', context)

def get_role_color(role_code):
    """Helper to return the specific color for each role as per design specs"""
    colors = {
        'SUPER_ADMIN': '#1E293B',
        'HEALTH_MGR': '#059669',
        'MAINT_SUP': '#EA580C',
        'WARDEN': '#7C3AED',
        'FINANCE': '#0D9488',
        'SECURITY': '#2563EB',
        'NEWS_EDITOR': '#DB2777',
        'AUDITOR': '#4B5563',
        'EMERGENCY': '#DC2626',
        'SUPPORT': '#0891B2',
        'DIPLOMA': '#D97706',
        'DEAN_HHS': '#78350F',
        'DEFERMENT': '#15803D',
        'DEPT_MCS': '#4338CA',
        'DVC_ASA': '#6B21A8',
    }
    return colors.get(role_code, '#64748b')

@login_required
@admin_only
def edit_staff(request, staff_id):
    """Edit a staff member's role and profile"""
    from .forms import StaffEditForm
    staff = get_object_or_404(StaffProfile, id=staff_id)
    if request.method == 'POST':
        form = StaffEditForm(request.POST, request.FILES, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, f"Profile for {staff.user.get_full_name()} updated.")
            return redirect('hms:manage_staff')
    else:
        form = StaffEditForm(instance=staff)
    return render(request, 'hms/rbac/edit_staff.html', {'form': form, 'staff': staff})

@login_required
@admin_only
def delete_staff(request, staff_id):
    """Delete a staff member and their user account"""
    staff = get_object_or_404(StaffProfile, id=staff_id)
    user = staff.user
    staff.delete()
    user.delete()
    messages.success(request, f"Staff account removed successfully.")
    return redirect('hms:manage_staff')


@login_required
@admin_only
def manage_roles(request):
    """Enterprise-grade Role Management Dashboard"""
    
    # Static data to simulate dynamic roles until full DB migration
    role_meta = {
        'SUPER_ADMIN': {'desc': 'Full system access – all modules', 'dept': 'Administration', 'perms': ['FULL', 'FULL', 'FULL', 'FULL', 'FULL', 'FULL', 'FULL', 'FULL', 'FULL', 'FULL', 'FULL']},
        'HEALTH_MGR': {'desc': 'Manage appointments, patients', 'dept': 'Medical', 'perms': ['NO', 'FULL', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO']},
        'MAINT_SUP': {'desc': 'Manage work orders, technicians', 'dept': 'Maintenance', 'perms': ['NO', 'NO', 'FULL', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO']},
        'WARDEN': {'desc': 'Manage accommodation, deferments', 'dept': 'Student Affairs', 'perms': ['NO', 'NO', 'NO', 'FULL', 'FULL', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO']},
        'FINANCE': {'desc': 'Manage payments, M-Pesa records', 'dept': 'Finance', 'perms': ['NO', 'NO', 'NO', 'NO', 'NO', 'FULL', 'NO', 'NO', 'NO', 'NO', 'NO']},
        'SECURITY': {'desc': 'Manage visitors, entry/exit logs', 'dept': 'Security', 'perms': ['NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'FULL', 'NO', 'NO', 'NO', 'NO']},
        'NEWS_EDITOR': {'desc': 'Create news, schedule posts', 'dept': 'Communications', 'perms': ['NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'FULL', 'NO', 'NO', 'NO']},
        'AUDITOR': {'desc': 'View audit logs only (read-only)', 'dept': 'Administration', 'perms': ['READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'NO']},
        'EMERGENCY': {'desc': 'Send emergency alerts', 'dept': 'Security', 'perms': ['NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'FULL', 'NO', 'NO']},
        'SUPPORT': {'desc': 'Manage student chats, tickets', 'dept': 'IT Support', 'perms': ['READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'NO', 'NO', 'NO', 'NO']},
        'DIPLOMA': {'desc': 'Manage diploma (TVET) students only', 'dept': 'Academic', 'perms': ['FULL', 'NO', 'NO', 'NO', 'FULL', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO']},
        'DEAN_HHS': {'desc': 'Manage student affairs and welfare', 'dept': 'Student Affairs', 'perms': ['FULL', 'READ', 'READ', 'READ', 'READ', 'NO', 'NO', 'READ', 'NO', 'NO', 'NO']},
        'DEFERMENT': {'desc': 'Process student deferment requests', 'dept': 'Academic', 'perms': ['READ', 'NO', 'NO', 'NO', 'FULL', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO']},
        'DEPT_MCS': {'desc': 'Manage computer science department', 'dept': 'Academic', 'perms': ['FULL', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO']},
        'DVC_ASA': {'desc': 'Deputy Vice Chancellor – Academic', 'dept': 'Administration', 'perms': ['FULL', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'NO']},
        'VC': {'desc': 'Vice Chancellor – Full staff view', 'dept': 'Executive', 'perms': ['FULL', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'NO']},
        'DVC': {'desc': 'Deputy Vice Chancellor – Full staff view', 'dept': 'Executive', 'perms': ['FULL', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'NO']},
        'REG_ADMIN': {'desc': 'Register Admin – View registered staff', 'dept': 'Administration', 'perms': ['READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'NO']},
        'REG_USER': {'desc': 'Register User – View registered staff', 'dept': 'Administration', 'perms': ['READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'READ', 'NO']},
        'DEAN_GRAD': {'desc': 'Dean Graduate School – Manage grad students', 'dept': 'Graduate School', 'perms': ['FULL', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO']},
        'DIR_RESOURCE': {'desc': 'Director Resource Mobilization – Funding', 'dept': 'Graduate School', 'perms': ['NO', 'NO', 'NO', 'NO', 'NO', 'FULL', 'NO', 'NO', 'NO', 'NO', 'NO']},
        'DIR_TVET': {'desc': 'Director TVET – Manage TVET department', 'dept': 'TVET', 'perms': ['FULL', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO']},
        'NEWS_AUDITOR': {'desc': 'News Auditor – Audit news/announcements', 'dept': 'Audit', 'perms': ['NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'READ', 'NO', 'READ', 'NO']},
        'librarian': {'desc': 'Manage library operations and books', 'dept': 'Library', 'perms': ['NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'FULL']}
    }

    modules = [
        'Student Management', 'Health Management', 'Maintenance Requests',
        'Accommodation', 'Deferment Management', 'Payments & M-Pesa',
        'Visitors Log', 'News & Alerts', 'Emergency Alerts', 'Audit Logs',
        'Library Management'
    ]

    roles = StaffProfile.ROLE_CHOICES
    
    role_stats = []
    total_permissions = 0
    assigned_roles = 0

    for role_code, role_name in roles:
        staff_in_role = StaffProfile.objects.filter(role=role_code).select_related('user')
        count = staff_in_role.count()
        if count > 0:
            assigned_roles += 1

        meta = role_meta.get(role_code, {'desc': '', 'dept': '', 'perms': ['NO']*11})
        total_permissions += sum(1 for p in meta['perms'] if p != 'NO')
        
        role_stats.append({
            'code': role_code,
            'name': role_name,
            'count': count,
            'color_hex': StaffProfile(role=role_code).get_role_color().get('hex', '#4B5563'),
            'desc': meta['desc'],
            'dept': meta['dept'],
            'perms': meta['perms'],
            'staff': staff_in_role,
        })
        
    staff_members = StaffProfile.objects.all().select_related('user')

    context = {
        'role_stats': role_stats,
        'modules': modules,
        'total_roles': len(roles),
        'active_roles': len(roles),
        'assigned_roles': assigned_roles,
        'total_permissions': total_permissions,
        'page_title': 'Role Management',
        'staff_members': staff_members,
        'total_staff': staff_members.count(),
        'active_count': staff_members.filter(user__is_active=True).count(),
        'pending_count': staff_members.filter(user__is_active=False).count(),
        'invited_count': 0,
        'role_count': len(roles),
    }
    return render(request, 'hms/rbac/manage_roles.html', context)


@login_required
@admin_only
def generate_staff_link(request):
    """Generate a secure, time-limited staff registration invitation link."""
    import secrets
    from datetime import timedelta
    generated_link = None
    expiry_hours = 24
    if request.method == 'POST':
        role = request.POST.get('role', '').strip()
        expiry_val = request.POST.get('expiry', '24h')
        usage_val = request.POST.get('usage', 'single')
        
        if role:
            token = secrets.token_urlsafe(32)
            
            # Determine expiry
            expires_at = None
            if expiry_val == '24h':
                expires_at = timezone.now() + timedelta(hours=24)
            elif expiry_val == '7d':
                expires_at = timezone.now() + timedelta(days=7)
            elif expiry_val == '30d':
                expires_at = timezone.now() + timedelta(days=30)
                
            # Determine usage limit
            usage_limit = 1
            if usage_val == 'multiple':
                usage_limit = 5
            elif usage_val == 'unlimited':
                usage_limit = 0
                
            invite = StaffInvitation.objects.create(
                token=token,
                role=role,
                expires_at=expires_at,
                usage_limit=usage_limit,
                created_by=request.user
            )
            
            generated_link = request.build_absolute_uri(
                f"/manage/staff/register/?invite={token}"
            )
            messages.success(request, f"Invitation link generated successfully.")
        else:
            messages.error(request, "Please select a role before generating a link.")
            
    # Need to add full_url to invitations for template
    invitations = StaffInvitation.objects.all().order_by('-created_at')
    for inv in invitations:
        inv.full_url = request.build_absolute_uri(f"/manage/staff/register/?invite={inv.token}")
        inv.is_expired = inv.expires_at and timezone.now() > inv.expires_at

    context = {
        'roles': StaffProfile.ROLE_CHOICES,
        'invitations': invitations,
        'generated_link': generated_link,
        'page_title': 'Staff Invitation System',
    }
    return render(request, 'hms/admin/generate_link.html', context)

@login_required
@admin_only
def manage_invitation_action(request, invite_id):
    """Handle actions for staff invitations (deactivate, delete, clear expired)"""
    action = request.GET.get('action')
    
    if action == 'clear_expired':
        expired = StaffInvitation.objects.filter(is_active=True).exclude(expires_at__isnull=True).filter(expires_at__lt=timezone.now())
        count = expired.count()
        expired.update(is_active=False)
        messages.success(request, f"Cleared {count} expired invitations.")
    elif invite_id and invite_id != 0:
        invite = get_object_or_404(StaffInvitation, id=invite_id)
        if action == 'deactivate':
            invite.is_active = False
            invite.save()
            messages.success(request, "Invitation deactivated successfully.")
        elif action == 'delete':
            invite.delete()
            messages.success(request, "Invitation deleted successfully.")
        elif action == 'email':
            email_address = request.GET.get('email')
            if email_address:
                try:
                    from django.core.mail import send_mail
                    from django.conf import settings
                    full_url = request.build_absolute_uri(f"/manage/staff/register/?invite={invite.token}")
                    
                    expires_text = invite.expires_at.strftime("%Y-%m-%d %H:%M") if invite.expires_at else "never"
                    usage_text = str(invite.usage_limit) if invite.usage_limit > 0 else "unlimited"
                    
                    role_display = dict(StaffProfile.ROLE_CHOICES).get(invite.role, invite.role)
                    
                    send_mail(
                        subject='Staff Invitation to Campus Care',
                        message=f'Hello,\n\nYou have been invited to join Campus Care as a {role_display}.\n\nPlease click the link below to register:\n{full_url}\n\nNote: This link expires on {expires_text} and can be used {usage_text} times.\n\nBest regards,\nCampus Care Admin',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email_address],
                        fail_silently=False,
                    )
                    messages.success(request, f"Email sent successfully to {email_address}.")
                except Exception as e:
                    messages.error(request, f"Failed to send email: {str(e)}")
            else:
                messages.error(request, "No email address provided.")
            
    return redirect('hms:generate_staff_link')

@login_required
@admin_only
def staff_details(request, staff_id):
    """Detailed view for a staff member"""
    staff = get_object_or_404(StaffProfile, id=staff_id)
    
    if request.method == 'POST' and 'approve_staff' in request.POST:
        if hasattr(request.user, 'staff_profile') and request.user.staff_profile.role == 'super_admin':
            staff.is_approved = True
            staff.save()
            messages.success(request, f"Staff account for {staff.user.get_full_name()} has been approved.")
            return redirect('hms:staff_details', staff_id=staff.id)
        else:
            messages.error(request, "Only Super Admins can approve staff accounts.")
            
    return render(request, 'hms/rbac/staff_details.html', {
        'staff': staff,
        'page_title': f"Staff Details: {staff.user.get_full_name()}"
    })

@login_required
@admin_only
def manual_register_staff(request):
    """Manually register a staff member without invitation link"""
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    staff = form.save()
                messages.success(request, f"Staff member {staff.user.get_full_name()} registered successfully!")
                return redirect('hms:manage_staff')
            except Exception as e:
                messages.error(request, f"Error creating staff: {str(e)}")
        else:
            for field, errors in form.errors.items():
                messages.error(request, f"{field}: {', '.join(errors)}")
    else:
        form = StaffRegistrationForm()

    return render(request, 'hms/admin/register_staff.html', {
        'form': form,
        'page_title': 'Manual Staff Registration',
        'is_manual': True
    })


@login_required
def notification_preferences(request):
    """Allow users to toggle their SMS/Email/WhatsApp notification preferences"""
    from .models import NotificationPreference
    prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        prefs.email_notifications = 'email_notifications' in request.POST
        prefs.sms_notifications = 'sms_notifications' in request.POST
        prefs.whatsapp_notifications = 'whatsapp_notifications' in request.POST
        prefs.save()
        messages.success(request, 'Notification preferences updated successfully!')
        return redirect('hms:notification_preferences')

    return render(request, 'hms/notification_preferences.html', {
        'prefs': prefs,
        'page_title': 'Notification Settings',
    })

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@login_required
def permission_matrix(request):
    """Permission matrix UI for Super Admins and Vice Chancellor"""
    if not request.user.is_superuser:
        staff_profile = getattr(request.user, 'staff_profile', None)
        if not staff_profile or staff_profile.role not in ['super_admin', 'vice_chancellor']:
            messages.error(request, 'Only Super Admins and the Vice Chancellor can view the permission matrix.')
            return redirect('hms:dashboard_redirect')
        
    from .models import StaffProfile, Permission, RolePermission
    roles = StaffProfile.ROLE_CHOICES
    permissions = Permission.objects.all().order_by('id')
    
    # Build nested dict: matrix[role][perm_code] = access_type
    matrix = {}
    for rp in RolePermission.objects.select_related('permission').all():
        if rp.role not in matrix:
            matrix[rp.role] = {}
        matrix[rp.role][rp.permission.code] = rp.access_type
    
    context = {
        'roles': roles,
        'permissions': permissions,
        'matrix_json': matrix,  # For json_script in template
        'page_title': 'Role Permission Matrix'
    }
    return render(request, 'hms/admin/permission_matrix.html', context)

@login_required
def save_permissions(request):
    """API endpoint to save permission matrix changes"""
    if not request.user.is_superuser:
        staff_profile = getattr(request.user, 'staff_profile', None)
        if not staff_profile or staff_profile.role != 'super_admin':
            return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
        
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    
    try:
        data = json.loads(request.body)
        perms_data = data.get('permissions', [])
        
        from .models import Permission, RolePermission
        
        # Clear all current permissions
        RolePermission.objects.all().delete()
        
        created_count = 0
        for p in perms_data:
            role = p.get('role')
            perm_code = p.get('permission_code')
            access = p.get('access', 'none')
            
            # Save full and read entries (skip 'none' as absence = no access)
            if access in ['full', 'read']:
                try:
                    perm_obj = Permission.objects.get(code=perm_code)
                    RolePermission.objects.create(role=role, permission=perm_obj, access_type=access)
                    created_count += 1
                except Permission.DoesNotExist:
                    continue
                    
        return JsonResponse({
            'status': 'success',
            'message': f'{created_count} permissions saved successfully.'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@super_admin_required
def feature_flags_control_panel(request):
    """View to render the Feature Flags Control Panel for super admins."""
    from .feature_flags import EXISTING_FEATURES, NEW_FEATURES, feature_flags
    
    existing_list = []
    for f in EXISTING_FEATURES:
        existing_list.append({
            'name': f['name'],
            'label': f['label'],
            'icon': f['icon'],
            'description': f['description'],
            'is_enabled': True
        })
        
    new_list = []
    for f in NEW_FEATURES:
        new_list.append({
            'name': f['name'],
            'label': f['label'],
            'icon': f['icon'],
            'description': f['description'],
            'is_enabled': feature_flags.is_enabled(f['name'])
        })
        
    context = {
        'existing_features': existing_list,
        'new_features': new_list,
        'page_title': 'Feature Flags Control Panel'
    }
    return render(request, 'hms/admin/feature_flags.html', context)


@login_required
@super_admin_required
def update_feature_flags_api(request):
    """API endpoint to toggle and update feature flag settings."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
        
    try:
        data = json.loads(request.body)
        action = data.get('action')
        
        from .feature_flags import NEW_FEATURES, feature_flags
        
        if action == 'toggle':
            name = data.get('name')
            enabled = data.get('enabled')
            if name is None or enabled is None:
                return JsonResponse({'status': 'error', 'message': 'Missing name or enabled parameter'}, status=400)
            
            feature_flags.set_enabled(name, bool(enabled))
            
            # Log to AuditLog
            AuditLog.objects.create(
                user=request.user,
                action='UPDATE',
                model_name='FeatureFlag',
                object_repr=f"Feature: {name}",
                details=json.dumps({'name': name, 'is_enabled': enabled})
            )
            return JsonResponse({'status': 'success', 'message': f"Feature '{name}' updated successfully."})
            
        elif action == 'enable_all':
            for f in NEW_FEATURES:
                feature_flags.set_enabled(f['name'], True)
            
            AuditLog.objects.create(
                user=request.user,
                action='UPDATE',
                model_name='FeatureFlag',
                object_repr="All Features Enabled",
                details="Enabled all toggleable features"
            )
            return JsonResponse({'status': 'success', 'message': 'All toggleable features enabled.'})
            
        elif action == 'disable_all':
            for f in NEW_FEATURES:
                feature_flags.set_enabled(f['name'], False)
                
            AuditLog.objects.create(
                user=request.user,
                action='UPDATE',
                model_name='FeatureFlag',
                object_repr="All Features Disabled",
                details="Disabled all toggleable features"
            )
            return JsonResponse({'status': 'success', 'message': 'All toggleable features disabled.'})
            
        elif action == 'reset':
            for f in NEW_FEATURES:
                feature_flags.set_enabled(f['name'], f['default'])
                
            AuditLog.objects.create(
                user=request.user,
                action='UPDATE',
                model_name='FeatureFlag',
                object_repr="Features Reset",
                details="Reset all toggleable features to defaults"
            )
            return JsonResponse({'status': 'success', 'message': 'Reset all toggleable features to default.'})
            
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)
            
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ============================================
# NEW FEATURES: ANALYTICS, MENTAL HEALTH, WHATSAPP
# ============================================
from .models import CounsellingRequest, MentalHealthResource, CrisisHelpline
import africastalking
from django.conf import settings
from django.http import HttpResponse

# --- WhatsApp Bot ---
try:
    africastalking.initialize(settings.AFRICASTALKING_USERNAME, settings.AFRICASTALKING_API_KEY)
    sms = africastalking.SMS
except Exception as e:
    print("Africa's Talking Init Error:", e)

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'POST':
        # AT webhook sends form-encoded data
        sender = request.POST.get('from', '')
        text = request.POST.get('text', '').strip().upper()
        
        # Phone number from WhatsApp format: "whatsapp:+2547XXXXXXXX"
        clean_phone = sender.replace('whatsapp:', '').strip()
        if clean_phone.startswith('+'):
            clean_phone = clean_phone[1:] # e.g. 2547...
            
        # Try to find student by phone
        student = Student.objects.filter(phone__icontains=clean_phone[-9:]).first()
        
        response_text = ""
        
        if not student:
            response_text = "Sorry, we could not find a student registered with this phone number. Please update your profile."
        else:
            if "BALANCE" in text:
                room_assignment = RoomAssignment.objects.filter(student=student, is_active=True).first()
                if room_assignment:
                    amount = room_assignment.room.price_per_semester
                    response_text = f"Your accommodation fee balance is KES {amount}. Pay via M-Pesa to Paybill {settings.MPESA_SHORTCODE}."
                else:
                    response_text = "You do not have any active room assignments or fee balances."
            elif "DEFERMENT" in text:
                latest_deferment = DefermentRequest.objects.filter(student=student).order_by('-created_at').first()
                if latest_deferment:
                    response_text = f"Your latest deferment application status is: {latest_deferment.get_status_display().upper()}"
                else:
                    response_text = "You have no pending deferment applications. Please apply via the portal."
            elif "STATUS" in text:
                latest_req = CounsellingRequest.objects.filter(student=student).order_by('-created_at').first()
                if latest_req:
                    response_text = f"Your latest counselling request status is: {latest_req.get_status_display().upper()}"
                else:
                    response_text = "No recent requests found."
            elif "HELP" in text:
                response_text = "Available commands:\n1. BALANCE - Check fee balance\n2. DEFERMENT - Check deferment status\n3. STATUS - Check general request status\n4. HELP - Show this menu"
            else:
                response_text = "Welcome to Campus Care Bot! Send 'HELP' to see available commands."
                
        # Send reply back via WhatsApp
        try:
            sms.send(response_text, [sender])
        except Exception as e:
            print("AT Send Error:", e)
            
        return HttpResponse("OK", status=200)
    return HttpResponse("Method not allowed", status=405)

def whatsapp_demo(request):
    return render(request, 'hms/whatsapp_demo.html')

# --- Analytics Dashboard (New Dedicated View) ---
@login_required
@permission_required('view_reports')
def new_analytics_dashboard(request):
    import json
    from django.db.models import Count
    
    total_students = Student.objects.count()
    
    # Calculate revenue (Completed payments)
    completed_payments = Payment.objects.filter(status='Completed')
    total_revenue = sum(p.amount for p in completed_payments)
    
    # Deferment approval rate
    total_def = DefermentRequest.objects.count()
    approved_def = DefermentRequest.objects.filter(status='approved').count()
    def_rate = round((approved_def / total_def * 100) if total_def > 0 else 0, 1)
    
    # Avg Response time (simplified logic)
    avg_response = "2.4 hours" # Mock for now
    
    # Line chart: 6-month request trends
    # Bar chart: Deferments by department
    depts = Student.objects.values('program_of_study').annotate(count=Count('deferment_requests')).order_by('-count')[:4]
    dept_labels = [d['program_of_study'] or 'Unknown' for d in depts]
    dept_data = [d['count'] for d in depts]
    
    # Pie chart: Payment methods
    payment_methods = {'M-Pesa': completed_payments.count(), 'Bank': 0, 'Cash': 0} # M-Pesa only currently
    
    chart_data = {
        'line_labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'line_data': [12, 19, 3, 5, 2, 3],
        'bar_labels': dept_labels if dept_labels else ['IT', 'Business', 'Engineering', 'Hospitality'],
        'bar_data': dept_data if sum(dept_data) > 0 else [10, 20, 15, 5],
        'pie_labels': list(payment_methods.keys()),
        'pie_data': list(payment_methods.values())
    }
    
    context = {
        'total_students': total_students,
        'total_revenue': total_revenue,
        'def_rate': def_rate,
        'avg_response': avg_response,
        'chart_data': json.dumps(chart_data)
    }
    return render(request, 'hms/admin/analytics.html', context)


# --- Mental Health Module ---
@login_required
def mental_health_dashboard(request):
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, "Only students can access this.")
        return redirect('hms:dashboard_redirect')
        
    requests = CounsellingRequest.objects.filter(student=student)
    resources = MentalHealthResource.objects.filter(is_active=True)
    helplines = CrisisHelpline.objects.filter(is_active=True)
    
    # Add seed data if empty
    if not resources.exists():
        MentalHealthResource.objects.create(title="Stress Management Guide", content="Learn to manage stress and balance your academics effectively.", resource_type="article")
        MentalHealthResource.objects.create(title="Guided Meditation", content="10 minute calming exercise to help you focus.", resource_type="audio")
        MentalHealthResource.objects.create(title="Peer Support Network", content="Connect with peers and share your experiences.", resource_type="contact")
        resources = MentalHealthResource.objects.all()
        
    if not helplines.exists():
        CrisisHelpline.objects.create(name="Campus Crisis Line", phone="0800 123 456", description="Available 24/7 for all students.", is_24hr=True)
        helplines = CrisisHelpline.objects.all()
        
    return render(request, 'hms/student/mental_health.html', {
        'requests': requests,
        'resources': resources,
        'helplines': helplines
    })

@login_required
def request_counselling(request):
    if request.method == 'POST':
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            student = None
            
        reason = request.POST.get('reason')
        urgency = request.POST.get('urgency', 'medium')
        is_anonymous = request.POST.get('is_anonymous') == 'on'
        pref_date = request.POST.get('preferred_date')
        
        req = CounsellingRequest.objects.create(
            student=student,
            is_anonymous=is_anonymous,
            reason=reason,
            urgency=urgency,
            preferred_date=pref_date if pref_date else None
        )
        messages.success(request, "Your counselling request has been submitted securely.")
        return redirect('hms:mental_health_dashboard')
    return redirect('hms:mental_health_dashboard')

@login_required
def counsellor_dashboard(request):
    if not hasattr(request.user, 'staff_profile') or request.user.staff_profile.role != 'counsellor':
        messages.error(request, "Access denied.")
        return redirect('hms:dashboard_redirect')
        
    all_reqs = CounsellingRequest.objects.all().order_by('-created_at')
    
    context = {
        'pending_count': all_reqs.filter(status='pending').count(),
        'in_progress_count': all_reqs.filter(status='in_progress').count(),
        'resolved_month': all_reqs.filter(status='resolved', updated_at__month=timezone.now().month).count(),
        'requests': all_reqs
    }
    return render(request, 'hms/rbac/counsellor_dashboard.html', context)

@login_required
def counselling_request_detail(request, pk):
    if not hasattr(request.user, 'staff_profile') or request.user.staff_profile.role != 'counsellor':
        messages.error(request, "Access denied.")
        return redirect('hms:dashboard_redirect')
        
    req = get_object_or_404(CounsellingRequest, pk=pk)
    
    if request.method == 'POST':
        req.status = request.POST.get('status', req.status)
        req.counsellor_notes = request.POST.get('counsellor_notes', req.counsellor_notes)
        req.assigned_counsellor = request.user
        req.save()
        messages.success(request, "Request updated.")
        return redirect('hms:counsellor_dashboard')
        
    return render(request, 'hms/admin/counselling_request_detail.html', {'req': req})



