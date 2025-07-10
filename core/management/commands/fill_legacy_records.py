from django.core.management.base import BaseCommand
from core.models import RecruitmentEmployee, LegacyRecruitmentRecord


class Command(BaseCommand):
    help = "Fill missing fields in LegacyRecruitmentRecord from RecruitmentEmployee"

    def handle(self, *args, **options):
        updated = 0

        for rec in LegacyRecruitmentRecord.objects.all().iterator():
            try:
                src = RecruitmentEmployee.objects.get(employee_number=rec.emp_id)
            except RecruitmentEmployee.DoesNotExist:
                continue

            changed = False

            if not rec.name_ar and src.name:
                rec.name_ar = src.name
                changed = True
            if not rec.name_en and src.name_en:
                rec.name_en = src.name_en
                changed = True
            if not rec.nationality and src.nationality:
                rec.nationality = src.nationality
                changed = True
            if not rec.profession and src.official_job:
                rec.profession = src.official_job
                changed = True
            if not rec.sponsor and src.sponsor_name:
                rec.sponsor = src.sponsor_name
                changed = True

            if changed:
                rec.save()
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"✅ تم تحديث {updated} سجلًا."))
