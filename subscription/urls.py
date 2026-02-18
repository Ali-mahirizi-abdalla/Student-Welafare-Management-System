from django.urls import path
from . import views

app_name = 'subscription'

urlpatterns = [
    path('', views.index, name='index'),
    path('pay/', views.payment, name='payment'),
    path('status/', views.status, name='status'),
]
