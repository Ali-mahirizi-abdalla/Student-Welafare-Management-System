from django.urls import path
from .views import ForgotPasswordView, ResetPasswordView
from .analytics import ActivityAnalyticsView

urlpatterns = [
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='api_forgot_password'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='api_reset_password'),
    path('analytics/activity/', ActivityAnalyticsView.as_view(), name='api_activity_analytics'),
]
