from django.test import TestCase
from django.db import IntegrityError
from django.utils import timezone
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import datetime
import io
import pandas as pd

from .models import (
    Learner,
    Nationality,
    Sector,
    Department,
    Section,
)
from .models import LegacyRecruitmentRecord, RecruitmentReport, RecruitmentEmployee


class LearnerModelTest(TestCase):
    """اختبارات قيود نموذج المتدرّب والعلاقات المرتبطة به."""

    def setUp(self):
        # كيانات مرجعية أساسية يستخدمها كل اختبار
        self.department = Department.objects.create(name="الإدارة")
        self.section = Section.objects.create(name="القسم", department=self.department)
        self.nationality = Nationality.objects.create(name="سعودي")
        self.sector = Sector.objects.create(name="القطاع")

    # دالة مساعدة لإنشاء متدرّب مع إمكانية تجاوز القيم الافتراضية
    def _create_learner(self, **kwargs):
        defaults = {
            "first_name_ar": "أحمد",
            "last_name_ar": "العلي",
            "first_name_en": "Ahmed",
            "last_name_en": "Alali",
            "department": self.department,
            "section": self.section,
            "nationality": self.nationality,
            "sector": self.sector,
            "manager": "مدير",
            "email": "unique@example.com",
            "national_id": "1234567890",
            "employee_number": "emp1",
        }
        defaults.update(kwargs)
        return Learner.objects.create(**defaults)

    # ----------------- اختبارات القيود الفريدة -----------------

    def test_email_unique_constraint(self):
        """يجب منع تكرار البريد الإلكتروني."""
        self._create_learner(email="test@example.com")
        with self.assertRaises(IntegrityError):
            self._create_learner(
                email="test@example.com",
                national_id="9876543210",
                employee_number="emp2",
            )

    def test_national_id_unique_constraint(self):
        """يجب منع تكرار رقم الهوية."""
        self._create_learner(national_id="123")
        with self.assertRaises(IntegrityError):
            self._create_learner(
                email="other@example.com",
                national_id="123",
                employee_number="emp3",
            )

    def test_employee_number_unique_constraint(self):
        """يجب منع تكرار الرقم الوظيفي."""
        self._create_learner(employee_number="777")
        with self.assertRaises(IntegrityError):
            self._create_learner(
                email="third@example.com",
                national_id="555",
                employee_number="777",
            )

    # ----------------- اختبارات العلاقات -----------------

    def test_manager_saved_as_text(self):
        """يجب حفظ اسم المدير كنص عادي."""
        learner = self._create_learner(manager="مدير تنفيذي")
        self.assertEqual(learner.manager, "مدير تنفيذي")

    def test_nationality_and_sector_relations(self):
        """يجب ربط الجنسية والقطاع بالكيانات المرجعية الصحيحة."""
        learner = self._create_learner()
        self.assertEqual(learner.nationality, self.nationality)
        self.assertEqual(learner.sector, self.sector)


class RecruitmentReportModelTest(TestCase):
    """اختبارات نموذج كشف الاستقدام."""

    def test_unique_together_constraint(self):
        """يجب منع تكرار الملف لنفس التاريخ ونوع الكشف."""
        from .models import RecruitmentReport

        dt = datetime.date(2024, 1, 1)
        RecruitmentReport.objects.create(
            filename="rep.xlsx",
            report_date=dt,
            file_size=1,
            is_haramain=False,
            columns=["col"],
            rows=[{"col": "x"}],
        )
        with self.assertRaises(IntegrityError):
            RecruitmentReport.objects.create(
                filename="rep.xlsx",
                report_date=dt,
                file_size=2,
                is_haramain=False,
                columns=["col"],
                rows=[{"col": "y"}],
            )

    def test_str_representation(self):
        from .models import RecruitmentReport

        dt = datetime.date(2024, 1, 2)
        rep = RecruitmentReport.objects.create(
            filename="file.xlsx",
            report_date=dt,
            file_size=1,
            is_haramain=True,
            columns=["c"],
            rows=[{"c": 1}],
        )
        self.assertEqual(str(rep), f"file.xlsx - {dt}")


class ImportReportRecordsTest(TestCase):
    """اختبار استيراد السجلات من الكشف المرفوع."""

    def setUp(self):
        from django.contrib.auth.models import User

        self.user = User.objects.create_user(username="u", password="p")
        self.report = RecruitmentReport.objects.create(
            filename="safety.xlsx",
            report_date=datetime.date(2024, 2, 1),
            file_size=1,
            is_haramain=False,
            columns=[
                "EMP NO",
                "Name Arabic",
                "Name English",
                "Passport No",
                "Nationality",
                "Actual Profession",
                "Sponsor Name",
            ],
            rows=[
                {
                    "EMP NO": "100",
                    "Name Arabic": "أحمد",
                    "Name English": "Ahmed",
                    "Passport No": "P1",
                    "Nationality": "SA",
                    "Actual Profession": "Worker",
                    "Sponsor Name": "ABC",
                }
            ],
        )

    def test_import_allows_duplicates(self):
        self.client.force_login(self.user)
        url = reverse("core:import_report_records", args=[self.report.pk])
        self.client.post(url)
        self.assertEqual(LegacyRecruitmentRecord.objects.count(), 1)
        # Second call should create a duplicate record
        self.client.post(url)
        self.assertEqual(LegacyRecruitmentRecord.objects.count(), 2)

    def test_import_arabic_headers(self):
        """Ensure Arabic column names are mapped correctly."""
        report = RecruitmentReport.objects.create(
            filename="arabic.xlsx",
            report_date=datetime.date(2024, 3, 1),
            file_size=1,
            is_haramain=False,
            columns=[
                "الرقم الوظيفي",
                "الاسم عربي",
                "الاسم انجليزي",
                "رقم الجواز",
                "الجنسية",
                "المهنة",
                "اسم الكفيل",
            ],
            rows=[
                {
                    "الرقم الوظيفي": "200",
                    "الاسم عربي": "سامي",
                    "الاسم انجليزي": "Sami",
                    "رقم الجواز": "P2",
                    "الجنسية": "EG",
                    "المهنة": "Engineer",
                    "اسم الكفيل": "XYZ",
                }
            ],
        )

        self.client.force_login(self.user)
        url = reverse("core:import_report_records", args=[report.pk])
        self.client.post(url)

        rec = LegacyRecruitmentRecord.objects.get(emp_id="200")
        self.assertEqual(rec.name_ar, "سامي")
        self.assertEqual(rec.name_en, "Sami")
        self.assertEqual(rec.passport_no, "P2")
        self.assertEqual(rec.nationality, "EG")
        self.assertEqual(rec.profession, "Engineer")
        self.assertEqual(rec.sponsor, "XYZ")


class UploadEmployeesUpdateTest(TestCase):
    """التأكد من تحديث السجلات الموجودة بدلاً من تكرارها."""

    def _excel_file(self, rows):
        buf = io.BytesIO()
        pd.DataFrame(rows).to_excel(buf, index=False)
        buf.seek(0)
        return SimpleUploadedFile(
            "rep.xlsx", buf.getvalue(), content_type="application/vnd.ms-excel"
        )

    def test_update_existing_employee(self):
        url = reverse("core:upload_employees")

        file1 = self._excel_file(
            [
                {
                    "serial": 1,
                    "employee_number": "10",
                    "name": "Ali",
                    "Evaluation": "The assessment cannot be conducted",
                },
            ]
        )
        self.client.post(
            url,
            {"report_date": "2024-01-01", "is_haramain": "false", "file": file1},
        )
        self.assertEqual(RecruitmentEmployee.objects.count(), 1)
        emp = RecruitmentEmployee.objects.get(employee_number="10")
        self.assertEqual(emp.name, "Ali")

        file2 = self._excel_file(
            [
                {"serial": 1, "employee_number": "10", "name": "Moh"},
            ]
        )
        self.client.post(
            url,
            {"report_date": "2024-01-02", "is_haramain": "false", "file": file2},
        )
        self.assertEqual(RecruitmentEmployee.objects.count(), 1)
        emp.refresh_from_db()
        self.assertEqual(emp.name, "Moh")


class UpdateDatabaseExportTest(TestCase):
    """Ensure exported file matches the legacy schema."""

    def test_export_all_columns(self):
        LegacyRecruitmentRecord.objects.create(
            employees="1",
            emp_id="100",
            name_ar="Ali",
        )

        url = reverse("core:update_database")
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)

        buf = io.BytesIO(resp.content)
        df = pd.read_excel(buf)

        expected = [
            "Employees",
            "Emp. ID",
            "Evaliuation",
            "Result",
            "Result Expectations",
            "Name (Arabic)",
            "Name (English)",
            "Passport No.",
            "Nationality",
            "Profession",
            "Profession Group",
            "Sponsor",
            "Date",
            "Month",
            "Month Number",
            "Sector",
            "Team Group",
            "Project",
            "Management",
            "Project Manager",
            "Director of Management",
            "Year",
        ]

        self.assertEqual(list(df.columns), expected)
        self.assertEqual(len(df), 1)


class UpdateDatabaseEmptyExportTest(TestCase):
    """Export should include columns even when no records exist."""

    def test_export_no_records(self):
        url = reverse("core:update_database")
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)

        buf = io.BytesIO(resp.content)
        df = pd.read_excel(buf)

        expected = [
            "Employees",
            "Emp. ID",
            "Evaliuation",
            "Result",
            "Result Expectations",
            "Name (Arabic)",
            "Name (English)",
            "Passport No.",
            "Nationality",
            "Profession",
            "Profession Group",
            "Sponsor",
            "Date",
            "Month",
            "Month Number",
            "Sector",
            "Team Group",
            "Project",
            "Management",
            "Project Manager",
            "Director of Management",
            "Year",
        ]

        self.assertEqual(list(df.columns), expected)
        self.assertEqual(len(df), 0)
