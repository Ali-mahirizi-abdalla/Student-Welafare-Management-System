from django.core.management.base import BaseCommand
from django.utils import timezone
from subscription.models import Subscription

class Command(BaseCommand):
    help = 'Check and expire subscriptions that have passed their end date'

    def handle(self, *args, **kwargs):
        now = timezone.now().date()
        subscriptions = Subscription.objects.filter(status='active', end_date__lt=now)
        
        count = 0
        for sub in subscriptions:
            sub.status = 'expired'
            sub.save()
            count += 1
            
        self.stdout.write(self.style.SUCCESS(f'Successfully expired {count} subscriptions'))
