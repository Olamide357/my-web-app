# vtu/management/commands/delete_old_transactions.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from base.models import Transaction  # adjust if Transaction is in another app

class Command(BaseCommand):
    help = "Delete transactions older than 2 weeks"

    def handle(self, *args, **kwargs):
        cutoff_date = timezone.now().date() - timedelta(weeks=2)
        old_transactions = Transaction.objects.filter(date__lt=cutoff_date)
        count = old_transactions.count()
        old_transactions.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} old transactions."))
