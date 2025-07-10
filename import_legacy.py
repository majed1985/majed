import pandas as pd
import re
from core.models import LegacyRecruitmentRecord

# Path to the Excel file to import. Adjust this before running.
EXCEL_FILE = 'legacy.xlsx'

# Mapping from Excel columns to LegacyRecruitmentRecord fields after cleaning
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

# Additional mappings for Arabic headers
ARABIC_COLUMN_MAP = {
    "الرقم الوظيفي": "emp_id",
    "الاسم عربي": "name_ar",
    "الاسم انجليزي": "name_en",
    "رقم الجواز": "passport_no",
    "الجنسية": "nationality",
    "المهنة": "profession",
    "اسم الكفيل": "sponsor",
}

# Unified map used for renaming
COLUMN_MAP = {**COLUMN_FIELD_MAP, **ARABIC_COLUMN_MAP}

# Characters sometimes hidden in Excel headers
INVISIBLE_CHARS = {'\u200f', '\ufeff'}


def clean_name(name: str) -> str:
    """Strip whitespace, punctuation, and invisible characters."""
    name = str(name)
    for ch in INVISIBLE_CHARS:
        name = name.replace(ch, '')
    name = name.strip()
    name = re.sub(r'[:\u0589\u061b]+$', '', name).strip()
    return name


def main():
    # Load the Excel file
    df = pd.read_excel(EXCEL_FILE)

    # Clean column names
    df.columns = [clean_name(c) for c in df.columns]

    # Rename columns to match model field names
    df.rename(columns=COLUMN_MAP, inplace=True)

    # Clean textual result values but keep all rows
    if 'result' in df.columns:
        df['result'] = df['result'].fillna('').apply(clean_name)
        df.loc[df['result'] == '', 'result'] = None

    # Convert evaluation to numeric when possible
    if 'evaluation' in df.columns:
        df['evaluation'] = pd.to_numeric(df['evaluation'], errors='coerce')

    # Determine model fields
    model_fields = {
        f.name for f in LegacyRecruitmentRecord._meta.get_fields()
        if f.concrete and not f.auto_created
    }

    records = []
    for row in df.to_dict(orient='records'):
        cleaned = {
            f: (None if pd.isna(row.get(f)) else row.get(f))
            for f in model_fields
        }
        if all(value is None for value in cleaned.values()):
            continue
        records.append(LegacyRecruitmentRecord(**cleaned))

    if records:
        LegacyRecruitmentRecord.objects.bulk_create(records)
        print(f'Imported {len(records)} records')
    else:
        print('No records imported')


if __name__ == '__main__':
    main()
