import os
import django
from datetime import date
from decimal import Decimal
from pathlib import Path

import pandas as pd

# Adjust these constants before running
EXCEL_FILE = 'data.xlsx'
DEFAULT_DATE = date(2025, 7, 10)
DEFAULT_SECTOR = 'حرمين'  # or 'غير حرمين'

# Map Excel headers to RecruitmentEmployee model fields
COLUMN_MAP = {
    'الرقم الوظيفي': 'employee_number',
    'Evaluation': 'evaluation',
    'Result': 'result',
    'Result Expectations': 'result_expectations',
    'الاسم عربي': 'name',
    'الاسم انجليزي': 'name_en',
    'رقم الجواز': 'passport_number',
    'الجنسية': 'nationality',
    'المهنة': 'official_job',
    'اسم الكفيل': 'sponsor_name',
    'التاريخ': 'start_date',
    'القطاع': 'sector',
    'السنة': 'year',
}

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import RecruitmentEmployee

# --------------------------------------------------------------------------------------

def clean_header(name: str) -> str:
    """Strip whitespace and remove hidden characters from column headers."""
    for ch in ('\u200f', '\ufeff'):
        name = name.replace(ch, '')
    return str(name).strip()


def read_excel(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df.columns = [clean_header(c) for c in df.columns]
    # Drop the serial column entirely if present
    for col in ['المسلسل', 'serial']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)
    # Rename to match model fields
    df.rename(columns=COLUMN_MAP, inplace=True)
    return df


def fill_missing_columns(df: pd.DataFrame) -> pd.DataFrame:
    if 'start_date' not in df:
        df['start_date'] = DEFAULT_DATE
    else:
        df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce').fillna(DEFAULT_DATE).dt.date

    if 'sector' not in df:
        df['sector'] = DEFAULT_SECTOR
    if 'year' not in df:
        df['year'] = pd.to_datetime(df['start_date']).dt.year

    df['is_haramain'] = df['sector'].astype(str).str.strip() == 'حرمين'
    return df


def import_rows(df: pd.DataFrame) -> int:
    model_fields = {
        f.name for f in RecruitmentEmployee._meta.get_fields()
        if f.concrete and not f.auto_created
    }
    records = []
    for row in df.to_dict(orient='records'):
        data = {k: row.get(k) for k in model_fields if k in row}
        # Convert decimals
        if data.get('evaluation') not in (None, ''):
            try:
                data['evaluation'] = Decimal(str(data['evaluation']))
            except Exception:
                data['evaluation'] = None
        if data.get('start_date') == '':
            data['start_date'] = None
        if not any(value not in (None, '') for value in data.values()):
            continue
        records.append(RecruitmentEmployee(**data))
    if records:
        RecruitmentEmployee.objects.bulk_create(records)
    return len(records)


def main():
    path = Path(EXCEL_FILE)
    if not path.exists():
        raise FileNotFoundError(path)

    df = read_excel(path)
    df = fill_missing_columns(df)

    count = import_rows(df)
    print(f"Imported {count} employees")


if __name__ == '__main__':
    main()
