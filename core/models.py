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
        verbose_name="الإدارة",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    section = models.ForeignKey(
        Section,
        verbose_name="القسم",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_learners",
        verbose_name="المدير المباشر",
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
