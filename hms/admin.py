from django.contrib import admin
from .models import (Student, Meal, Activity, AwayPeriod, Announcement, 
                     MaintenanceRequest, LeaveRequest, AuditLog, 
                     Room, RoomAssignment, RoomChangeRequest, Payment, 
                     Notification, LoginActivity, Visitor)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'university_id', 'phone', 'is_warden')
    search_fields = ('user__username', 'university_id', 'phone')

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'breakfast', 'early', 'supper', 'away')
    list_filter = ('date', 'breakfast', 'supper', 'away')
    search_fields = ('student__user__username', 'student__university_id')

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'weekday', 'time', 'active')
    list_filter = ('weekday', 'active')

@admin.register(AwayPeriod)
class AwayPeriodAdmin(admin.ModelAdmin):
    list_display = ('student', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'is_active', 'created_by', 'created_at')
    list_filter = ('priority', 'is_active', 'created_at')
    search_fields = ('title', 'content')

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'priority', 'status', 'created_at')
    list_filter = ('priority', 'status', 'created_at')
    search_fields = ('title', 'description', 'student__user__username')

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'floor', 'block', 'room_type', 'capacity', 'is_available')
    list_filter = ('floor', 'block', 'room_type', 'is_available')
    search_fields = ('room_number', 'block')

@admin.register(RoomAssignment)
class RoomAssignmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'room', 'bed_number', 'assigned_date', 'is_active')
    list_filter = ('is_active', 'assigned_date')
    search_fields = ('student__user__username', 'room__room_number')

@admin.register(RoomChangeRequest)
class RoomChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'current_room', 'requested_room', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('student__user__username', 'reason')

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'deferment_type', 'start_date', 'end_date', 'status')
    list_filter = ('deferment_type', 'status', 'start_date')
    search_fields = ('student__user__username', 'reason')

@admin.register(LoginActivity)
class LoginActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'timestamp', 'status')
    list_filter = ('timestamp', 'status')
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('user', 'ip_address', 'user_agent', 'timestamp', 'status')

    def has_add_permission(self, request):
        return False

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'model_name', 'object_repr', 'user', 'timestamp')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('object_repr', 'details', 'user__username', 'ip_address')
    readonly_fields = ('user', 'model_name', 'object_id', 'object_repr', 'action', 'details', 'ip_address', 'user_agent', 'timestamp')
    actions = ['export_as_csv']

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False # Logs should be immutable ideally

    @admin.action(description='Export Selected Logs to CSV')
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'transaction_id', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('student__user__username', 'transaction_id', 'phone_number')
    readonly_fields = ('transaction_id', 'checkout_request_id', 'created_at')

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('name', 'student', 'check_in_time', 'check_out_time', 'is_active')
    list_filter = ('is_active', 'check_in_time')
    search_fields = ('name', 'student__user__username', 'id_number')
