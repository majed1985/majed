from django.db import models
from django.contrib.auth.models import User


class Nationality(models.Model):
    name = models.CharField("الجنسية", max_length=30, unique=True)

    def __str__(self) -> str:
        return self.name


class Sector(models.Model):
    name = models.CharField("القطاع", max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name


class Department(models.Model):
    name = models.CharField("الإدارة", max_length=50, unique=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Section(models.Model):
    name = models.CharField("القسم", max_length=50)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name="الإدارة",
    )
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("department", "name")
        verbose_name = "القسم"
        verbose_name_plural = "الأقسام"

    def __str__(self) -> str:
        return f"{self.department.name} - {self.name}"


class Learner(models.Model):
    # --- الخطوة 1: المعلومات الشخصية ---
    first_name_ar = models.CharField("الاسم الأول (ع)", max_length=30)
    last_name_ar = models.CharField("اسم العائلة (ع)", max_length=30)
    first_name_en = models.CharField("First Name (En)", max_length=30)
    last_name_en = models.CharField("Last Name (En)", max_length=30)

    # --- الخطوة 2: المعلومات الوظيفية ---
    employee_number = models.CharField(
        "الرقم الوظيفي",
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="الإدارة",
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="القسم",
    )
    manager = models.CharField(
        "المدير المباشر",
        max_length=50,
        null=True,
        blank=True,
    )

    # --- الخطوة 3: معلومات التواصل ---
    email = models.EmailField(
        "البريد الإلكتروني",
        unique=True,
        null=True,
        blank=True,
        db_index=True,
    )
    mobile = models.CharField("رقم الجوال", max_length=20, null=True, blank=True)
    national_id = models.CharField(
        "رقم الهوية",
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
    )
    nationality = models.ForeignKey(
        Nationality,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="الجنسية",
    )
    sector = models.ForeignKey(
        Sector,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="القطاع",
    )

    # --- الخطوة 4: ربط المستخدم ---
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)

    # --- بيانات إضافية ---
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "متدرّب"
        verbose_name_plural = "المتدرّبون"

    def __str__(self) -> str:
        return f"{self.first_name_ar} {self.last_name_ar}"


class RecruitmentEmployee(models.Model):
    """موظفو الاستقدام الحديث المستوردون من ملفات Excel."""

    name = models.CharField("الاسم", max_length=100)
    nationality = models.CharField("الجنسية", max_length=50)
    official_job = models.CharField("المهنة الرسمية", max_length=100)
    actual_job = models.CharField("المهنة الفعلية", max_length=100)
    computer_number = models.CharField("رقم الكمبيوتر", max_length=50)
    project_name = models.CharField("اسم المشروع", max_length=100)
    start_date = models.DateField("تاريخ المباشرة")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "موظف استقدام"
        verbose_name_plural = "موظفو الاستقدام"

    def __str__(self) -> str:
        return self.name


class EmployeeEvaluation(models.Model):
    """تقييم موظف الاستقدام بعد المحاضرة التعريفية والتقييم العملي."""

    employee = models.ForeignKey(
        RecruitmentEmployee,
        on_delete=models.CASCADE,
        related_name="evaluations",
        verbose_name="الموظف",
    )
    appearance_score = models.PositiveSmallIntegerField("المظهر")
    experience_score = models.PositiveSmallIntegerField("الخبرة")
    skills_score = models.PositiveSmallIntegerField("المهارات الفنية")
    notes = models.TextField("ملاحظات", blank=True)
    evaluator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="المقيّم",
    )
    evaluation_photo = models.ImageField(
        upload_to="evaluation_photos/",
        null=True,
        blank=True,
        verbose_name="صورة التقييم",
    )
    orientation_photo = models.ImageField(
        upload_to="orientation_photos/",
        null=True,
        blank=True,
        verbose_name="صورة المحاضرة",
    )
    evaluated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تقييم موظف"
        verbose_name_plural = "تقييمات الموظفين"

    def __str__(self) -> str:
        return f"{self.employee.name} - {self.evaluator}" if self.evaluator else self.employee.name

