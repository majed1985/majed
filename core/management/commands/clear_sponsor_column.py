from django.core.management.base import BaseCommand
from core.models import LegacyRecruitmentRecord


class Command(BaseCommand):
    help = "Clear sponsor values for the first 33822 legacy records"

    def handle(self, *args, **options):
        ids = list(
            LegacyRecruitmentRecord.objects.order_by("id")
            .values_list("id", flat=True)[:33822]
        )
        if not ids:
            self.stdout.write("No records found")
            return

        updated = LegacyRecruitmentRecord.objects.filter(id__in=ids).update(sponsor=None)
        self.stdout.write(self.style.SUCCESS(f"Cleared sponsor for {updated} records"))

