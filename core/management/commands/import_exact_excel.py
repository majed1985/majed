from django.core.management.base import BaseCommand
from core.models import LegacyRecruitmentRecord
from django.db import models
import pandas as pd
import re

# Some Excel editors include invisible characters in the column headers. If we
# don't strip them, the names won't match the model field names and values will
# be lost. This helper mimics the cleaning logic used in other import scripts.
INVISIBLE_CHARS = {
    "\u200f",  # RTL mark
    "\ufeff",  # BOM
}

# Mapping from cleaned Excel columns to model field names
COLUMN_FIELD_MAP = {
    "Employees": "employees",
    "Emp. ID": "emp_id",
    "Evaliuation": "evaluation",
    "Result": "result",
    "Result Expectations": "result_expectations",
    "Name (Arabic)": "name_ar",
    "Name (English)": "name_en",
    "Passport No.": "passport_no",
    "Nationality": "nationality",
    "Profession": "profession",
    "Profession Group": "profession_group",
    "Sponsor": "sponsor",
    "Sponsor Name": "sponsor",
    "Spensor": "sponsor",
    "Spensor Name": "sponsor",
    "اسبنسور": "sponsor",
    "الاسبنسور": "sponsor",
    "سبونسر": "sponsor",
    "السبونسر": "sponsor",
    "Date": "date",
    "Month": "month",
    "Month Number": "month_number",
    "Sector": "sector",
    "Team Group": "team_group",
    "Project": "project",
    "Management": "management",
    "Project Manager": "project_manager",
    "Director of Management": "director_of_management",
    "Year": "year",
}

# Additional mappings for Arabic column headers
ARABIC_COLUMN_MAP = {
    "الرقم الوظيفي": "emp_id",
    "الاسم عربي": "name_ar",
    "الاسم انجليزي": "name_en",
    "رقم الجواز": "passport_no",
    "الجنسية": "nationality",
    "المهنة": "profession",
    "اسم الكفيل": "sponsor",
    "اسبنسور": "sponsor",
    "الاسبنسور": "sponsor",
    "سبونسر": "sponsor",
    "السبونسر": "sponsor",
}

# Combine both maps for renaming
COLUMN_MAP = {**COLUMN_FIELD_MAP, **ARABIC_COLUMN_MAP}


def clean_name(name: str) -> str:
    name = str(name)
    for ch in INVISIBLE_CHARS:
        name = name.replace(ch, "")
    name = name.strip()
    name = re.sub(r"[:\u0589\u061b]+$", "", name).strip()
    name = re.sub(r"\.\d+$", "", name)
    return name


def truncate_record(rec: LegacyRecruitmentRecord) -> None:
    for field in rec._meta.get_fields():
        if isinstance(field, models.CharField):
            val = getattr(rec, field.name)
            if isinstance(val, str) and field.max_length and len(val) > field.max_length:
                setattr(rec, field.name, val[: field.max_length])


class Command(BaseCommand):
    help = "Import LegacyRecruitmentRecord rows from an Excel file when column names match model fields."

    def add_arguments(self, parser):
        parser.add_argument("excel_file", help="Path to the Excel file")

    def handle(self, *args, **options):
        path = options["excel_file"]
        df = pd.read_excel(path)
        df.columns = [clean_name(c) for c in df.columns]
        df.rename(columns=COLUMN_MAP, inplace=True)

        sponsor_indices = [i for i, col in enumerate(df.columns) if col == "sponsor"]

        if "result" in df.columns:
            df["result"] = df["result"].fillna("").apply(clean_name)
            df.loc[df["result"] == "", "result"] = None
        if "evaluation" in df.columns:
            df["evaluation"] = pd.to_numeric(df["evaluation"], errors="coerce")

        model_fields = {
            f.name
            for f in LegacyRecruitmentRecord._meta.get_fields()
            if f.concrete and not f.auto_created
        }

        records = []
        for _, row in df.iterrows():
            cleaned = {}
            for f in model_fields:
                if f == "sponsor":
                    continue
                val = row.get(f)
                cleaned[f] = None if pd.isna(val) else val

            sponsor_value = None
            for idx in sponsor_indices:
                if idx < len(row):
                    val = row.iloc[idx]
                    if val not in ("", None) and not (isinstance(val, float) and pd.isna(val)):
                        sponsor_value = val
                        break
            cleaned["sponsor"] = sponsor_value

            if all(value is None for value in cleaned.values()):
                continue
            rec = LegacyRecruitmentRecord(**cleaned)
            truncate_record(rec)
            records.append(rec)

        if records:
            LegacyRecruitmentRecord.objects.bulk_create(records)
            self.stdout.write(self.style.SUCCESS(f"Imported {len(records)} records"))
        else:
            self.stdout.write("No records imported")
