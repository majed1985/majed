import pandas as pd
import re
from core.models import LegacyRecruitmentRecord

def clean_text(val):
    if pd.isna(val):
        return ""
    if not isinstance(val, str):
        val = str(val)
    # احذف الرموز التالفة نهائيًا
    val = val.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
    # (اختياري) نظف أي رموز غريبة أخرى باستثناء العربية والإنجليزية والأرقام وبعض الرموز العامة
    val = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFFa-zA-Z0-9\s\-_.,:/()]+', '', val)
    return val.strip()

file_path = r"C:\Users\engma\Desktop\majed2\data.xlsx"
df = pd.read_excel(file_path)

df = df.rename(columns={
    'Employees': 'employees',
    'Emp. ID': 'emp_id',
    'Evaluation': 'evaluation',
    'Result': 'result',
    'Result Expectations': 'result_expectations',
    'Name (Arabic)': 'name_ar',
    'Name (English)': 'name_en',
    'Passport No.': 'passport_no',
    'Nationality': 'nationality',
    'Profession': 'profession',
    'Profession Groub': 'profession_group',
    'sponsor': 'sponsor',
    'Date': 'date',
    'Month': 'month',
    'Month Number': 'month_number',
    'Sector': 'sector',
    'Team Group': 'team_group',
    'Project': 'project',
    'Management': 'management',
    'Project Manager': 'project_manager',
    'Director of Management': 'director_of_management',
    'Year': 'year'
})

records = []
for _, row in df.iterrows():
    emp_id = clean_text(row.get("emp_id", ""))
    if not emp_id:
        continue
    rec = LegacyRecruitmentRecord(
        employees=clean_text(row.get("employees", "")),
        emp_id=emp_id,
        evaluation=clean_text(row.get("evaluation", "")),
        result=clean_text(row.get("result", "")),
        result_expectations=clean_text(row.get("result_expectations", "")),
        name_ar=clean_text(row.get("name_ar", "")),
        name_en=clean_text(row.get("name_en", "")),
        passport_no=clean_text(row.get("passport_no", "")),
        nationality=clean_text(row.get("nationality", "")),
        profession=clean_text(row.get("profession", "")),
        profession_group=clean_text(row.get("profession_group", "")),
        sponsor=clean_text(row.get("sponsor", "")),
        date=clean_text(row.get("date", "")),
        month=clean_text(row.get("month", "")),
        month_number=clean_text(row.get("month_number", "")),
        sector=clean_text(row.get("sector", "")),
        team_group=clean_text(row.get("team_group", "")),
        project=clean_text(row.get("project", "")),
        management=clean_text(row.get("management", "")),
        project_manager=clean_text(row.get("project_manager", "")),
        director_of_management=clean_text(row.get("director_of_management", "")),
        year=clean_text(row.get("year", ""))
    )
    records.append(rec)

LegacyRecruitmentRecord.objects.all().delete()  # لحذف كل البيانات القديمة قبل الإضافة
LegacyRecruitmentRecord.objects.bulk_create(records)
print(f"تمت إضافة {len(records)} سجل بنجاح.")
