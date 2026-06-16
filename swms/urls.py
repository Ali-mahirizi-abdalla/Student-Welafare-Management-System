from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from subscription.views import intasend_webhook

urlpatterns = [
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('library/', include('library.urls')),
    path('v1/events/', intasend_webhook, name='intasend_webhook'),
    path('v1/events', intasend_webhook),  # Handle without trailing slash too
    path('', include('hms.urls', namespace='hms')),
]

# Custom error handlers
handler403 = 'hms.views.access_denied'
handler404 = 'hms.views.page_not_found'


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)