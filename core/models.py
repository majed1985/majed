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

    # ترتيب الحقول بحسب الكشف الورقي
    serial = models.PositiveIntegerField("التسلسل", null=True, blank=True)
    employee_number = models.CharField(
        "الرقم الوظيفي", max_length=50, db_index=True
    )
    name = models.CharField("الاسم عربي", max_length=100)
    name_en = models.CharField(
        "الاسم انجليزي", max_length=100, blank=True, null=True
    )
    passport_number = models.CharField(
        "رقم الجواز", max_length=100, blank=True, null=True
    )
    nationality = models.CharField("الجنسية", max_length=50, blank=True, null=True)
    official_job = models.CharField("المهنة", max_length=100, blank=True, null=True)
    sponsor_name = models.CharField(
        "اسم الكفيل", max_length=100, blank=True, null=True
    )

    # تقييم ونتائج
    evaluation = models.DecimalField(
        "Evaluation", max_digits=5, decimal_places=2, null=True, blank=True
    )
    result = models.CharField("Result", max_length=100, blank=True, null=True)
    result_expectations = models.CharField(
        "Result Expectations", max_length=100, blank=True, null=True
    )

    # حقول إضافية كانت موجودة مسبقاً
    start_date = models.DateField("تاريخ المباشرة", null=True, blank=True)
    is_haramain = models.BooleanField("حرمين", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    report = models.ForeignKey(
        "RecruitmentReport",
        on_delete=models.CASCADE,
        related_name="employees",
        verbose_name="الكشف",
        null=True,
        blank=True,
    )
    final_score = models.DecimalField(
        "الدرجة النهائية", max_digits=5, decimal_places=2, null=True, blank=True
    )
    evaluation_date = models.DateField(
        "تاريخ آخر تقييم", null=True, blank=True
    )

    class Meta:
        verbose_name = "موظف استقدام"
        verbose_name_plural = "موظفو الاستقدام"

    def __str__(self) -> str:
        return self.name

    @property
    def last_evaluation_date(self):
        """Return stored evaluation date or date of the most recent evaluation."""
        if self.evaluation_date:
            return self.evaluation_date
        evaluation = self.evaluations.order_by("-evaluated_at").first()
        return evaluation.evaluated_at.date() if evaluation else None


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
    is_haramain = models.BooleanField("حرمين", default=False)
    evaluated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تقييم موظف"
        verbose_name_plural = "تقييمات الموظفين"

    def __str__(self) -> str:
        return f"{self.employee.name} - {self.evaluator}" if self.evaluator else self.employee.name


class RecruitmentReport(models.Model):
    """تمثيل كشف استقدام كامل كما هو مرفوع من ملف Excel."""

    filename = models.CharField("اسم الملف", max_length=255)
    uploaded_at = models.DateTimeField("تاريخ الرفع", auto_now_add=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="تم الرفع بواسطة",
    )
    report_date = models.DateField("تاريخ الكشف")
    file_size = models.PositiveIntegerField("حجم الملف (بايت)", default=0)
    is_haramain = models.BooleanField("حرمين", default=False)
    columns = models.JSONField("الأعمدة")
    rows = models.JSONField("الصفوف")

    class Meta:
        unique_together = ("filename", "report_date", "is_haramain")
        verbose_name = "كشف استقدام"
        verbose_name_plural = "كشوف الاستقدام"

    def __str__(self) -> str:
        return f"{self.filename} - {self.report_date}"


class LegacyRecruitmentRecord(models.Model):
    """سجل قديم لبيانات الاستقدام."""

    employees = models.CharField("Employees", max_length=100)
    emp_id = models.CharField("Emp. ID", max_length=50)
    evaluation = models.DecimalField(
        "Evaliuation", max_digits=5, decimal_places=2, null=True, blank=True
    )
    result = models.CharField("Result", max_length=100, null=True, blank=True)
    result_expectations = models.CharField(
        "Result Expectations", max_length=100, null=True, blank=True
    )
    name_ar = models.CharField("Name (Arabic)", max_length=100, null=True, blank=True)
    name_en = models.CharField("Name (English)", max_length=100, null=True, blank=True)
    passport_no = models.CharField("Passport No.", max_length=100, null=True, blank=True)
    nationality = models.CharField("Nationality", max_length=50, null=True, blank=True)
    profession = models.CharField("Profession", max_length=100, null=True, blank=True)
    profession_group = models.CharField(
        "Profession Group", max_length=100, null=True, blank=True
    )
    sponsor = models.CharField("Sponsor", max_length=100, null=True, blank=True)
    date = models.DateField("Date", null=True, blank=True)
    month = models.CharField("Month", max_length=20, null=True, blank=True)
    month_number = models.PositiveSmallIntegerField(
        "Month Number", null=True, blank=True
    )
    sector = models.CharField("Sector", max_length=100, null=True, blank=True)
    team_group = models.CharField("Team Group", max_length=100, null=True, blank=True)
    project = models.CharField("Project", max_length=100, null=True, blank=True)
    management = models.CharField("Management", max_length=100, null=True, blank=True)
    project_manager = models.CharField(
        "Project Manager", max_length=100, null=True, blank=True
    )
    director_of_management = models.CharField(
        "Director of Management", max_length=100, null=True, blank=True
    )
    year = models.PositiveIntegerField("Year", null=True, blank=True)

    class Meta:
        verbose_name = "سجل استقدام قديم"
        verbose_name_plural = "سجلات الاستقدام القديمة"

    def __str__(self) -> str:
        return f"{self.emp_id} - {self.name_ar or self.name_en}".strip()

