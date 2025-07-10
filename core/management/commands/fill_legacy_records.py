from django.core.management.base import BaseCommand
from core.models import RecruitmentEmployee, LegacyRecruitmentRecord


class Command(BaseCommand):
    help = "يستكمل الحقول الفارغة في LegacyRecruitmentRecord من RecruitmentEmployee"

    def handle(self, *args, **options):
        qs = LegacyRecruitmentRecord.objects.filter(name_ar__isnull=True)
        updated = 0

        for rec in qs:
            try:
                src = RecruitmentEmployee.objects.get(employee_number=rec.employee_number)
            except RecruitmentEmployee.DoesNotExist:
                continue

            rec.name_ar = src.name
            rec.name_en = src.name_en
            rec.nationality = src.nationality
            rec.profession = src.official_job
            rec.sponsor = src.sponsor_name
            rec.save()
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"✅ تم تحديث {updated} سجلًّا."))
