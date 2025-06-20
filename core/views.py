# core/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
import re
from openpyxl import load_workbook
import pandas as pd
from django.utils import timezone
import datetime
from django.views.decorators.http import require_POST
import os

from .models import (
    Learner,
    Nationality,
    Sector,
    Department,
    Section,
    RecruitmentEmployee,
    EmployeeEvaluation,
)

from .forms import UploadEmployeesForm, EmployeeEvaluationForm


# ---------------------------------------------------------------------------
def home(request):
    """الصفحة الرئيسية (تُظهر بطاقة المتدرّب عند تسجيل الدخول)."""
    learner = (
        Learner.objects.filter(user=request.user).first()
        if request.user.is_authenticated
        else None
    )
    return render(request, "core/home.html", {"learner": learner})


# ---------------------------------------------------------------------------
def recruitment_dashboard(request):
    """الواجهة الرئيسية لخطوات تقييم موظفي الاستقدام."""
    print("Rendering template: core/recruitment_dashboard.html")
    print("Template absolute path:", os.path.abspath(__file__))
    return render(request, "core/recruitment_dashboard.html")


def recruitment_placeholder(request, page):
    """صفحات مبدئية لكل مرحلة."""
    return render(request, "core/recruitment_placeholder.html", {"page": page})


# ---------------------------------------------------------------------------
def register(request):
    """تسجيل متدرّب جديد ثم إرسال رابط التفعيل إلى بريده الإلكتروني."""

    if request.method == "POST":
        data = request.POST
        errors = []

        # -------- تحقّق من الحقول المطلوبة ------------------------------------
        required_fields = {
            "first_name_ar": "الاسم الأول (عربي)",
            "last_name_ar": "اسم العائلة (عربي)",
            "first_name_en": "First Name (English)",
            "last_name_en": "Last Name (English)",
            "employee_number": "الرقم الوظيفي",
            "department": "الإدارة",
            "section": "القسم",
            "email": "البريد الإلكتروني",
            "password": "كلمة المرور",
            "confirm_password": "تأكيد كلمة المرور",
        }
        for field, label in required_fields.items():
            if not data.get(field):
                errors.append(f"حقل «{label}» مطلوب")

        # -------- تحقّقات إضافية --------------------------------------------
        if data.get("email") and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", data["email"]):
            errors.append("صيغة البريد الإلكتروني غير صحيحة")

        if data.get("national_id") and not re.fullmatch(r"\d{10}", data["national_id"]):
            errors.append("رقم الهوية يجب أن يتكوّن من 10 أرقام")

        if data.get("password") != data.get("confirm_password"):
            errors.append("كلمة المرور غير متطابقة")

        if User.objects.filter(username=data.get("email")).exists():
            errors.append("هذا البريد الإلكتروني مستخدم بالفعل")

        # -------- في حال وجود أخطاء ------------------------------------------
        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, "core/register.html", status=200)

        # ---------------------------------------------------------------------
        # إنشاء المستخدم (مُعطَّل لحين التفعيل)
        user = User.objects.create_user(
            username=data["email"],
            email=data["email"],
            password=data["password"],
            is_active=False,
        )

        # ----- حفظ الإدارة والقسم كعلاقات فعلية --------------------------------
        dept_name = data.get("department", "").strip()
        sect_name = data.get("section", "").strip()
        nat_name  = data.get("nationality", "").strip()
        sectr_name= data.get("sector", "").strip()

        department = None
        if dept_name:
            department, _ = Department.objects.get_or_create(name=dept_name)

        section = None
        if sect_name and department:
            section, _ = Section.objects.get_or_create(
                name=sect_name,
                department=department,
            )

        nationality = None
        if nat_name:
            nationality, _ = Nationality.objects.get_or_create(name=nat_name)
        sector = None
        if sectr_name:
            sector, _ = Sector.objects.get_or_create(name=sectr_name)

        manager_name = data.get("manager", "").strip()

        # إنشاء سجل المتدرّب مع العلاقات المرجعية
        Learner.objects.create(
            first_name_ar=data["first_name_ar"],
            last_name_ar=data["last_name_ar"],
            first_name_en=data["first_name_en"],
            last_name_en=data["last_name_en"],
            employee_number=data["employee_number"],
            department=department,
            section=section,
            manager=manager_name,
            email=data["email"],
            mobile=data.get("mobile", ""),
            national_id=data.get("national_id", ""),
            nationality=nationality,
            sector=sector,
            user=user,
        )

        # -------- إرسال رسالة التفعيل ----------------------------------------
        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = f"http://{current_site.domain}{reverse('core:activate', args=[uid, token])}"

        subject = "تفعيل الحساب"
        message = (
            "مرحباً،\n"
            "لإكمال التسجيل يرجى الضغط على الرابط التالي:\n"
            f"{activation_link}"
        )
        send_mail(subject, message, None, [user.email])

        messages.success(
            request,
            "تم إنشاء الحساب بنجاح. يرجى التحقق من بريدك الإلكتروني لتفعيله.",
        )
        return redirect("core:register_thanks")

    # GET
    return render(request, "core/register.html")


# ---------------------------------------------------------------------------
def register_thanks(request):
    """صفحة الشكر بعد إنشاء الحساب."""
    return render(request, "core/register_thanks.html")


# ---------------------------------------------------------------------------
def activate(request, uidb64, token):
    """تفعيل الحساب عند الضغط على رابط البريد."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "تم تفعيل الحساب بنجاح، يمكنك تسجيل الدخول الآن.")
        return redirect("core:login")

    return render(request, "core/activation_invalid.html", status=400)


# ---------------------------------------------------------------------------
def login_view(request):
    """تسجيل الدخول للمستخدمين المفعّلين."""
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("core:home")

    if form.errors:
        messages.error(request, "اسم المستخدم أو كلمة المرور غير صحيحة")

    return render(request, "core/login.html", {"form": form})


# ---------------------------------------------------------------------------
def other_services(request):
    """عرض صفحة الخدمات الأخرى مع كروت الخدمات."""
    return render(request, "core/other_services.html")


# ---------------------------------------------------------------------------
def service_page(request, service):
    """عرض صفحة خدمة معينة بناءً على الاسم الممرر."""
    # صفحة "أعمالي" لها قالب مخصص يعرض كروت الخدمات
    if service == "my_works":
        return render(request, "core/my_works.html")

    service_names = {
        "needs_analysis": "تحليل الاحتياجات التدريبية",
        "share_knowledge": "شاركنا المعرفة",
        "youtube_tracks": "مسارات دورات اليوتيوب",
        "skills_program": "برنامج مهارات",
        "articles": "مقالات",
        "my_certificates": "شهاداتي",
        "course_announcements": "إعلانات الدورات التدريبية",
        "my_works": "أعمالي",
    }

    name = service_names.get(service, service)
    context = {"service_name": name}
    return render(request, "core/service_page.html", context)


# ---------------------------------------------------------------------------
def upload_employees(request):
    """تحميل ملف Excel واستيراد بيانات الموظفين."""
    if request.method == "POST":
        form = UploadEmployeesForm(request.POST, request.FILES)
        if form.is_valid():
            is_haramain = form.cleaned_data["is_haramain"] == "true"
            df = pd.read_excel(
                form.cleaned_data["excel_file"],
                header=None,
                skiprows=1,
            )
            for values in df.itertuples(index=False):
                row = list(values)
                if not any(pd.notna(cell) for cell in row):
                    continue
                RecruitmentEmployee.objects.create(
                    serial=row[0],
                    employee_number=str(row[1]),
                    name=row[2],
                    name_en=row[3],
                    passport_number=row[4],
                    nationality=row[5],
                    official_job=row[6],
                    sponsor_name=row[7],
                    evaluation=row[8],
                    result=row[9],
                    result_expectations=row[10],
                    start_date=timezone.localdate(),
                    is_haramain=is_haramain,
                    final_score=row[8] if pd.notna(row[8]) else None,
                )
            messages.success(request, "تم استيراد الموظفين بنجاح")
            return redirect("core:upload_employees")
    else:
        form = UploadEmployeesForm()
    employees = RecruitmentEmployee.objects.all().order_by("-created_at")

    grouped = {}
    for emp in employees:
        dt = timezone.localtime(emp.created_at).date()
        grouped.setdefault(dt.year, {}).setdefault(dt.month, {}).setdefault(dt.day, []).append(emp)

    sorted_grouped = []
    for year in sorted(grouped.keys(), reverse=True):
        months = []
        for month in sorted(grouped[year].keys(), reverse=True):
            days = []
            for day in sorted(grouped[year][month].keys(), reverse=True):
                days.append({"day": day, "employees": grouped[year][month][day]})
            months.append({"month": month, "days": days})
        sorted_grouped.append({"year": year, "months": months})

    return render(
        request,
        "core/upload_employees.html",
        {"form": form, "grouped": sorted_grouped},
    )


# ---------------------------------------------------------------------------
def evaluate_employee(request, pk):
    """تعبئة استمارة تقييم موظف معين."""
    employee = RecruitmentEmployee.objects.get(pk=pk)
    if request.method == "POST":
        form = EmployeeEvaluationForm(request.POST, request.FILES)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.employee = employee
            evaluation.evaluator = request.user if request.user.is_authenticated else None
            evaluation.is_haramain = employee.is_haramain
            evaluation.save()
            messages.success(request, "تم حفظ التقييم")
            return redirect("core:evaluate_employee", pk=employee.pk)
    else:
        form = EmployeeEvaluationForm()
    return render(
        request,
        "core/evaluate_employee.html",
        {"form": form, "employee": employee},
    )


@require_POST
def set_final_score(request, pk):
    """تعديل الدرجة النهائية لموظف معين."""
    employee = RecruitmentEmployee.objects.get(pk=pk)
    score = request.POST.get("final_score")
    try:
        employee.final_score = float(score)
    except (TypeError, ValueError):
        pass
    else:
        employee.save()
    return redirect("core:upload_employees")

# ---------------------------------------------------------------------------
def input_evaluation_results(request):
    """إدخال الدرجات لعدد من الموظفين دفعة واحدة."""
    employees = RecruitmentEmployee.objects.all().order_by("created_at")

    grouped = {}
    for emp in employees:
        dt = timezone.localtime(emp.created_at).date()
        grouped.setdefault(dt.year, {}).setdefault(dt.month, {}).setdefault(dt.day, []).append(emp)

    year = request.GET.get("year")
    month = request.GET.get("month")
    day = request.GET.get("day")
    selected = []

    if request.method == "POST":
        year = request.POST.get("year")
        month = request.POST.get("month")
        day = request.POST.get("day")
        try:
            y = int(year)
            m = int(month)
            d = int(day)
            selected = grouped.get(y, {}).get(m, {}).get(d, [])
        except (TypeError, ValueError):
            selected = []
        for emp in selected:
            score = request.POST.get(f"score_{emp.id}")
            if score:
                try:
                    emp.final_score = float(score)
                    emp.save()
                except ValueError:
                    pass
        messages.success(request, "تم حفظ الدرجات")
        return redirect(f"{reverse('core:input_evaluation_results')}?year={year}&month={month}&day={day}")
    else:
        try:
            y = int(year)
            m = int(month)
            d = int(day)
            selected = grouped.get(y, {}).get(m, {}).get(d, [])
        except (TypeError, ValueError):
            selected = []

    years = sorted(grouped.keys(), reverse=True)
    months = sorted(grouped.get(int(year), {}).keys(), reverse=True) if year and year.isdigit() else []
    days = sorted(grouped.get(int(year), {}).get(int(month), {}).keys(), reverse=True) if year and month and year.isdigit() and month.isdigit() else []

    context = {
        "years": years,
        "months": months,
        "days": days,
        "selected_year": year,
        "selected_month": month,
        "selected_day": day,
        "employees": selected,
    }
    return render(request, "core/input_results.html", context)
