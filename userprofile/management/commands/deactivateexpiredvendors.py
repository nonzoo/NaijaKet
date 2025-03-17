from django.core.management.base import BaseCommand
from django.utils.timezone import now
from datetime import timedelta
from userprofile.models import Userprofile

class Command(BaseCommand):
    help = "Deactivate expired vendor subscriptions"

    def handle(self, *args, **kwargs):
        expiration_date = now() - timedelta(days=30)
        expired_vendors = Userprofile.objects.filter(is_vendor=True, subscription_date__lte=expiration_date)

        for vendor in expired_vendors:
            vendor.is_vendor = False
            vendor.subscription_date = None
            vendor.save()
            self.stdout.write(self.style.SUCCESS(f"Deactivated vendor: {vendor.user.username}"))
