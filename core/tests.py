from django.test import TestCase
from django.db import IntegrityError

from .models import (
    Learner,
    Nationality,
    Sector,
    Department,
    Section,
)


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

