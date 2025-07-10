from django.core.management.base import BaseCommand
from core.models import LegacyRecruitmentRecord
import pandas as pd
import re

# Some Excel editors include invisible characters in the column headers. If we
# don't strip them, the names won't match the model field names and values will
# be lost. This helper mimics the cleaning logic used in other import scripts.
INVISIBLE_CHARS = {
    "\u200f",  # RTL mark
    "\ufeff",  # BOM
}

# Minimal column mapping for known sponsor aliases
COLUMN_MAP = {
    "Sponsor": "sponsor",
    "Sponsor Name": "sponsor",
    "Spensor": "sponsor",
    "Spensor Name": "sponsor",
    "اسبنسور": "sponsor",
    "الاسبنسور": "sponsor",
    "سبونسر": "sponsor",
    "السبونسر": "sponsor",
}


def clean_name(name: str) -> str:
    name = str(name)
    for ch in INVISIBLE_CHARS:
        name = name.replace(ch, "")
    name = name.strip()
    name = re.sub(r"[:\u0589\u061b]+$", "", name).strip()
    name = re.sub(r"\.\d+$", "", name)
    return name


class Command(BaseCommand):
    help = "Import LegacyRecruitmentRecord rows from an Excel file when column names match model fields."

    def add_arguments(self, parser):
        parser.add_argument("excel_file", help="Path to the Excel file")

    def handle(self, *args, **options):
        path = options["excel_file"]
        df = pd.read_excel(path)
        df.columns = [clean_name(c) for c in df.columns]
        df.rename(columns=COLUMN_MAP, inplace=True)

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
            cleaned = {k: v for k, v in data.items() if k in model_fields}
            LegacyRecruitmentRecord.objects.create(**cleaned)
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {count} records"))
