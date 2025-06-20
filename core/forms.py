# core/forms.py
from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import FileInput


class ClearableMultipleFileInput(forms.ClearableFileInput):
    """Allow selecting multiple files with Django's clearable input."""

    allow_multiple_selected = True

    def __init__(self, attrs=None):
        attrs = attrs or {}
        attrs["multiple"] = True
        FileInput.__init__(self, attrs)

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
    file = forms.FileField(
        label="كشف الاستقدام (Excel)",
        widget=ClearableMultipleFileInput(
            attrs={"class": "w-full border border-gray-300 rounded-md p-2"}
        ),
    )
    HARAMAIN_CHOICES = [
        ("true", "حرمين"),
        ("false", "غير حرمين"),
    ]
    is_haramain = forms.ChoiceField(
        choices=HARAMAIN_CHOICES,
        label="نوع الكشف",
        widget=forms.Select(attrs={"class": "w-full border border-gray-300 rounded-md p-2"}),
    )
    report_date = forms.DateField(
        label="تاريخ الكشف",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "w-full border border-gray-300 rounded-md p-2",
            }
        ),
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
        widgets = {
            "appearance_score": forms.NumberInput(
                attrs={
                    "class": "w-full border-2 border-gray-300 rounded px-3 py-2",
                    "placeholder": "0-10",
                }
            ),
            "experience_score": forms.NumberInput(
                attrs={
                    "class": "w-full border-2 border-gray-300 rounded px-3 py-2",
                    "placeholder": "0-10",
                }
            ),
            "skills_score": forms.NumberInput(
                attrs={
                    "class": "w-full border-2 border-gray-300 rounded px-3 py-2",
                    "placeholder": "0-10",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "w-full border-2 border-gray-300 rounded px-3 py-2",
                    "rows": 3,
                    "placeholder": "اكتب أي ملاحظات...",
                }
            ),
            "evaluation_photo": forms.ClearableFileInput(
                attrs={"class": "w-full"}
            ),
            "orientation_photo": forms.ClearableFileInput(
                attrs={"class": "w-full"}
            ),
        }
        help_texts = {
            "appearance_score": "قيّم المظهر من 0 إلى 10.",
            "experience_score": "قيّم الخبرة من 0 إلى 10.",
            "skills_score": "قيّم المهارات من 0 إلى 10.",
            "evaluation_photo": "ارفع صورة أثناء التقييم إن وجدت.",
            "orientation_photo": "ارفع صورة من المحاضرة التعريفية إن وجدت.",
        }

