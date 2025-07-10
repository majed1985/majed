from django.core.management.base import BaseCommand
from core.models import LegacyRecruitmentRecord
import pandas as pd


class Command(BaseCommand):
    help = "Import LegacyRecruitmentRecord rows from an Excel file when column names match model fields."

    def add_arguments(self, parser):
        parser.add_argument("excel_file", help="Path to the Excel file")

    def handle(self, *args, **options):
        path = options["excel_file"]
        df = pd.read_excel(path)

        model_fields = {
            f.name
            for f in LegacyRecruitmentRecord._meta.get_fields()
            if f.concrete and not f.auto_created and f.name != "id"
        }

        count = 0
        for _, row in df.iterrows():
            if row.isna().all():
                continue
            data = row.to_dict()
            if "Sponsor" in data and "sponsor" not in data:
                data["sponsor"] = data["Sponsor"]
            cleaned = {k: v for k, v in data.items() if k in model_fields}
            LegacyRecruitmentRecord.objects.create(**cleaned)
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {count} records"))
