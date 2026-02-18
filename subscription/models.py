from django.db import models
from django.utils import timezone
from datetime import timedelta

class Subscription(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('pending', 'Pending'),
    )
    
    PLAN_CHOICES = (
        ('monthly', 'Monthly - KES 3,000'),
    )

    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='monthly')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.start_date and not self.end_date:
            self.end_date = self.start_date + timedelta(days=30)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.plan} - {self.status}"
