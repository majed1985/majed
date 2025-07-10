from django.core.management.base import BaseCommand
from core.models import LegacyRecruitmentRecord


class Command(BaseCommand):
    help = "Delete empty LegacyRecruitmentRecord entries"

    def handle(self, *args, **options):
        fields = [
            f.name
            for f in LegacyRecruitmentRecord._meta.get_fields()
            if f.concrete and not f.auto_created and f.name != "id"
        ]

        ids = []
        for rec in LegacyRecruitmentRecord.objects.all().iterator():
            values = [getattr(rec, f) for f in fields]
            if all(v in (None, "") for v in values):
                ids.append(rec.id)

        if ids:
            LegacyRecruitmentRecord.objects.filter(id__in=ids).delete()
            self.stdout.write(
                self.style.SUCCESS(f"Deleted {len(ids)} empty records")
            )
        else:
            self.stdout.write("No empty records found")

