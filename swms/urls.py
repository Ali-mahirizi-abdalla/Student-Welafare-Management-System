from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

from subscription.views import intasend_webhook
from hms.views import landing_page

urlpatterns = [
    path('', landing_page, name='landing'),
    path('google17891a7c3e3a6e03.html', lambda r: HttpResponse("google-site-verification: google17891a7c3e3a6e03.html", content_type="text/html")),
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