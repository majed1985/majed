# core/forms.py
from django import forms
from django.contrib.auth.models import User

from .models import Learner, Nationality, Sector
from .models import RecruitmentEmployee, EmployeeEvaluation


# ـــــــ الخطوة 1: المعلومات الشخصية ـــــــ #
class LearnerStep1Form(forms.ModelForm):
    class Meta:
        model = Learner
        fields = [
            "first_name_ar",
            "last_name_ar",
            "first_name_en",
            "last_name_en",
        ]


# ـــــــ الخطوة 2: المعلومات الوظيفية ـــــــ #
class LearnerStep2Form(forms.ModelForm):
    class Meta:
        model = Learner
        fields = [
            "employee_number",
            "department",
            "section",
            "manager",
        ]


# ـــــــ الخطوة 3: معلومات التواصل ـــــــ #
class LearnerStep3Form(forms.ModelForm):
    class Meta:
        model = Learner
        fields = [
            "email",
            "mobile",
            "national_id",
            "nationality",
            "sector",
        ]


# ـــــــ الخطوة 4: إنشاء حساب المستخدم ـــــــ #
class LearnerStep4Form(forms.ModelForm):
    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(render_value=False),
    )
    confirm_password = forms.CharField(
        label="تأكيد كلمة المرور",
        widget=forms.PasswordInput(render_value=False),
    )

    class Meta:
        model = User
        fields = ["username", "password"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password and confirm and password != confirm:
            raise forms.ValidationError("كلمتا المرور غير متطابقتين")

        return cleaned_data


class UploadEmployeesForm(forms.Form):
    excel_file = forms.FileField(label="ملف Excel")
    HARAMAIN_CHOICES = [
        ("true", "حرمين"),
        ("false", "غير حرمين"),
    ]
    is_haramain = forms.ChoiceField(
        choices=HARAMAIN_CHOICES,
        label="نوع الكشف",
        widget=forms.Select(),
    )


class RecruitmentReportForm(forms.Form):
    file = forms.FileField(label="كشف الاستقدام (Excel)")
    report_date = forms.DateField(
        label="تاريخ الكشف",
        widget=forms.DateInput(attrs={"type": "date"}),
    )


class EmployeeEvaluationForm(forms.ModelForm):
    class Meta:
        model = EmployeeEvaluation
        fields = [
            "appearance_score",
            "experience_score",
            "skills_score",
            "notes",
            "evaluation_photo",
            "orientation_photo",
        ]

