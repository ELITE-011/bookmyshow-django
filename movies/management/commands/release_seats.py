from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from movies.models import Booking


class Command(BaseCommand):
    help = "Release expired seat reservations"

    def handle(self, *args, **kwargs):

        expired_time = timezone.now() - timedelta(minutes=5)

        expired_bookings = Booking.objects.filter(
            payment_status="Pending",
            reserved_at__lt=expired_time
        )

        count = expired_bookings.count()

        expired_bookings.delete()

        self.stdout.write(
            self.style.SUCCESS(f"{count} expired bookings deleted.")
        )