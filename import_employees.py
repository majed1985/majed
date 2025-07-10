import os
import django
from datetime import date
from decimal import Decimal
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Adjust these constants before running
EXCEL_FILE = 'data.xlsx'
DEFAULT_DATE = date(2025, 7, 10)
DEFAULT_SECTOR = 'حرمين'  # or 'غير حرمين'

# Map original Excel headers to our internal names
COLUMN_MAP = {
    'الرقم الوظيفي': 'emp_id',
    'الاسم عربي': 'name_ar',
    'الاسم انجليزي': 'name_en',
    'المهنة': 'profession',
    'رقم الجواز': 'passport_no',
    'الجنسية': 'nationality',
    'اسم الكفيل': 'sponsor',
    'Evaluation': 'evaluation',
    'Result': 'result',
    'Result Expectations': 'result_expectations',
    'التاريخ': 'date',
    'القطاع': 'sector',
    'السنة': 'year',
}

# Mapping from internal names to `RecruitmentEmployee` model fields
FIELD_MAP = {
    'emp_id': 'employee_number',
    'name_ar': 'name',
    'name_en': 'name_en',
    'profession': 'official_job',
    'passport_no': 'passport_number',
    'nationality': 'nationality',
    'sponsor': 'sponsor_name',
    'evaluation': 'evaluation',
    'result': 'result',
    'result_expectations': 'result_expectations',
    'date': 'start_date',
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
    # Remove unwanted columns such as the serial number
    for col in list(df.columns):
        if clean_header(col) in ('المسلسل', 'serial'):
            df.drop(columns=[col], inplace=True)
    # Rename to our internal names
    df.rename(columns=COLUMN_MAP, inplace=True)

    unknown = [c for c in df.columns if c not in COLUMN_MAP.values()]
    if unknown:
        print(f"تحذير: سيتم تجاهل الأعمدة غير المعروفة: {', '.join(unknown)}")
        df.drop(columns=unknown, inplace=True)

    # Keep only columns that have a mapping
    df = df[[c for c in df.columns if c in COLUMN_MAP.values()]]
    return df


def fill_missing_columns(df: pd.DataFrame) -> pd.DataFrame:
    if 'date' not in df:
        df['date'] = DEFAULT_DATE
    else:
        df['date'] = (
            pd.to_datetime(df['date'], errors='coerce')
            .fillna(DEFAULT_DATE)
            .dt.date
        )

    if 'sector' not in df:
        df['sector'] = DEFAULT_SECTOR
    if 'year' not in df:
        df['year'] = pd.to_datetime(df['date']).dt.year

    df['is_haramain'] = df['sector'].astype(str).str.strip() == 'حرمين'
    return df


def import_rows(df: pd.DataFrame) -> int:
    count = 0
    for idx, row in df.iterrows():
        data = {}
        for col, model_field in FIELD_MAP.items():
            if col in row:
                data[model_field] = row[col]

        # handle decimal conversion
        if data.get('evaluation') not in (None, ''):
            try:
                data['evaluation'] = Decimal(str(data['evaluation']))
            except Exception:
                print(f"خطأ في الصف {idx + 1}: قيمة evaluation غير صالحة")
                continue

        data['is_haramain'] = str(row.get('sector', '')).strip() == 'حرمين'

        if data.get('start_date') == '':
            data['start_date'] = None

        try:
            RecruitmentEmployee.objects.create(**data)
            count += 1
        except Exception as e:
            print(f"خطأ في الصف {idx + 1}: {e}")
    return count


def main():
    path = Path(EXCEL_FILE)
    if not path.exists():
        raise FileNotFoundError(path)

    df = read_excel(path)
    df = fill_missing_columns(df)

    count = import_rows(df)
    print(f"تمت إضافة {count} سجلًا")


if __name__ == '__main__':
    main()
