from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from .models import Subscription
from django.contrib import messages

def index(request):
    # Check if already active
    today = timezone.now().date()
    active_sub = Subscription.objects.filter(status='active', end_date__gte=today).first()
    if active_sub:
        return redirect('subscription:status')
        
    return render(request, 'subscription/index.html')

def payment(request):
    if request.method == 'POST':
        # Simulate payment success
        Subscription.objects.create(
            plan='monthly',
            status='active',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
            amount_paid=3000.00,
            payment_date=timezone.now(),
            transaction_id=f"PAY-{int(timezone.now().timestamp())}"
        )
        messages.success(request, 'Payment Successful! Subscription Active.')
        return redirect('subscription:status')
    return redirect('subscription:index')

def status(request):
    today = timezone.now().date()
    # Get the latest subscription
    sub = Subscription.objects.order_by('-created_at').first()
    
    is_active = False
    if sub and sub.status == 'active' and sub.end_date >= today:
        is_active = True
        
    return render(request, 'subscription/status.html', {
        'subscription': sub,
        'is_active': is_active
    })
