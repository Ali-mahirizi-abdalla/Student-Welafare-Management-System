from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta, datetime
from hms.models import Student, Payment, MaintenanceRequest, Visitor, Meal
import collections

class ActivityAnalyticsView(APIView):
    """
    API endpoint to provide activity data for the dashboard chart.
    Supports daily, weekly, and monthly ranges.
    """
    def get(self, request):
        time_range = request.query_params.get('range', 'weekly')
        end_date = timezone.now().date()
        
        if time_range == 'daily':
            days = 1
            labels = ['Today']
            start_date = end_date
        elif time_range == 'monthly':
            days = 30
            start_date = end_date - timedelta(days=29)
            labels = [(start_date + timedelta(days=i)).strftime('%b %d') for i in range(30)]
        else: # weekly
            days = 7
            start_date = end_date - timedelta(days=6)
            labels = [(start_date + timedelta(days=i)).strftime('%a') for i in range(7)]

        data_points = []
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            data_points.append(current_date)

        def get_daily_counts(queryset, date_field, date_list):
            from django.db.models.functions import TruncDate
            counts = queryset.filter(**{f"{date_field}__date__in": date_list}) \
                             .annotate(day=TruncDate(date_field)) \
                             .values('day') \
                             .annotate(count=Count('id'))
            
            mapping = {str(item['day']): item['count'] for item in counts}
            return [mapping.get(str(d), 0) for d in date_list]

        # Specialized meal count logic
        meal_counts = Meal.objects.filter(date__in=data_points) \
                                .values('date') \
                                .annotate(count=Count('id'))
        meal_mapping = {str(item['date']): item['count'] for item in meal_counts}
        weekly_meals = [meal_mapping.get(str(d), 0) for d in data_points]

        # Fetch datasets
        weekly_registrations = get_daily_counts(Student.objects, 'user__date_joined', data_points)
        weekly_payments = get_daily_counts(Payment.objects.filter(status='completed'), 'created_at', data_points)
        weekly_maintenance = get_daily_counts(MaintenanceRequest.objects, 'created_at', data_points)
        weekly_visitors = get_daily_counts(Visitor.objects, 'check_in_time', data_points)

        # KPI Logic: Calculate actual percentage change
        previous_start_date = start_date - timedelta(days=days)
        previous_data_points = []
        for i in range(days):
            previous_data_points.append(previous_start_date + timedelta(days=i))

        # Helper for previous range total
        def get_total_for_range(date_list):
            reg = Student.objects.filter(user__date_joined__date__in=date_list).count()
            pay = Payment.objects.filter(status='completed', created_at__date__in=date_list).count()
            main = MaintenanceRequest.objects.filter(created_at__date__in=date_list).count()
            vis = Visitor.objects.filter(check_in_time__date__in=date_list).count()
            mel = Meal.objects.filter(date__in=date_list).count()
            return reg + pay + main + vis + mel

        total_activity = sum(weekly_registrations) + sum(weekly_payments) + \
                        sum(weekly_maintenance) + sum(weekly_visitors) + sum(weekly_meals)
        
        previous_total = get_total_for_range(previous_data_points)
        
        if previous_total == 0:
            pct_change = 100 if total_activity > 0 else 0
        else:
            pct_change = round(((total_activity - previous_total) / previous_total) * 100, 1)

        # Calculate Peak Day
        daily_totals = [
            weekly_registrations[i] + weekly_payments[i] + weekly_maintenance[i] + \
            weekly_visitors[i] + weekly_meals[i]
            for i in range(days)
        ]
        peak_index = daily_totals.index(max(daily_totals)) if daily_totals and any(daily_totals) else 0
        peak_day = labels[peak_index] if any(daily_totals) else "No Activity"

        response_data = {
            'labels': labels,
            'datasets': {
                'registrations': weekly_registrations,
                'payments': weekly_payments,
                'maintenance': weekly_maintenance,
                'visitors': weekly_visitors,
                'meals': weekly_meals,
            },
            'kpis': {
                'total_activity': total_activity,
                'peak_day': peak_day,
                'pct_change': pct_change,
            }
        }

        return Response(response_data)
