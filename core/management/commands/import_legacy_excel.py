from django.core.management.base import BaseCommand
from core.models import LegacyRecruitmentRecord
import pandas as pd

# Mapping from cleaned Excel columns to model field names
COLUMN_FIELD_MAP = {
    'Employees': 'employees',
    'Emp. ID': 'emp_id',
    'Evaliuation': 'evaluation',
    'Result': 'result',
    'Result Expectations': 'result_expectations',
    'Name (Arabic)': 'name_ar',
    'Name (English)': 'name_en',
    'Passport No.': 'passport_no',
    'Nationality': 'nationality',
    'Profession': 'profession',
    'Profession Group': 'profession_group',
    'Sponsor': 'sponsor',
    'Date': 'date',
    'Month': 'month',
    'Month Number': 'month_number',
    'Sector': 'sector',
    'Team Group': 'team_group',
    'Project': 'project',
    'Management': 'management',
    'Project Manager': 'project_manager',
    'Director of Management': 'director_of_management',
    'Year': 'year',
}

INVISIBLE_CHARS = {
    '\u200f',  # RTL mark
    '\ufeff',  # BOM
}


def clean_name(name: str) -> str:
    """Remove invisible characters and strip whitespace."""
    for ch in INVISIBLE_CHARS:
        name = name.replace(ch, '')
    return name.strip()


class Command(BaseCommand):
    help = 'Import legacy recruitment records from an Excel file.'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', help='Path to the Excel file to import')

    def handle(self, *args, **options):
        path = options['excel_file']

        df = pd.read_excel(path)
        df.columns = [clean_name(c) for c in df.columns]
        df = df.rename(columns={k: v for k, v in COLUMN_FIELD_MAP.items() if k in df.columns})

        model_fields = {f.name for f in LegacyRecruitmentRecord._meta.get_fields()
                        if f.concrete and not f.auto_created}

        records = []
        for row in df.to_dict(orient='records'):
            cleaned = {f: (None if pd.isna(row.get(f)) else row.get(f)) for f in model_fields}
            # Skip completely empty rows
            if all(value is None for value in cleaned.values()):
                continue
            records.append(LegacyRecruitmentRecord(**cleaned))

        if records:
            LegacyRecruitmentRecord.objects.bulk_create(records)
            self.stdout.write(self.style.SUCCESS(f'Imported {len(records)} records'))
        else:
            self.stdout.write('No records imported')
