from __future__ import annotations

import calendar
import datetime
import logging
import re
from decimal import Decimal

import pandas as pd
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.defaultfilters import filesizeformat
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.http import require_POST, require_http_methods

from .forms import (
    EmployeeEvaluationForm,
    RecruitmentReportEditForm,
    RecruitmentReportForm,
)
from .models import (
    Department,
    Learner,
    Nationality,
    RecruitmentEmployee,
    RecruitmentReport,
    LegacyRecruitmentRecord,
    Sector,
    Section,
)

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# أسماء الأعمدة المقبولة في ملفات الإكسل
# ------------------------------------------------------------------------------
EMPLOYEE_COLUMN_MAP: dict[str, list[str]] = {
    "serial":              ["serial", "التسلسل"],
    "employee_number": [
        "employee_number",
        "الرقم الوظيفي",
        "Employees",
        "Emp. ID",
        "Emp ID",
        "EMP ID",
        "EMP NO",
        "Emp No",
        "Emp No.",
        "EmpID",
        "EMP_NO",
    ],
    "name":                ["name", "الاسم عربي", "الاسم"],
    "name_en":             ["name_en", "الاسم انجليزي"],
    "passport_number":     ["passport_number", "رقم الجواز"],
    "nationality":         ["nationality", "الجنسية"],
    "official_job":        ["official_job", "المهنة"],
    "sponsor_name":        [
        "sponsor_name",
        "sponsor",
        "sponsor name",
        "spensor",
        "spensor name",
        "Spensor",
        "Spensor Name",
        "Sponsor",
        "Sponsor Name",
        "اسم الكفيل",
        "اسبنسور",
        "الاسبنسور",
        "سبونسر",
        "السبونسر",
    ],
    "evaluation":          ["evaluation", "Evaluation"],
    "result":              ["result", "Result"],
    "result_expectations": ["result_expectations", "Result Expectations"],
    "start_date":          ["start_date", "تاريخ المباشرة"],
}

# ------------------------------------------------------------------------------
# أعمدة كشف السلامة لاستيراد السجلات القديمة
# ------------------------------------------------------------------------------
LEGACY_COLUMN_MAP = {
    # English headers (مطابقة لما ظهر في ملفك الحالي)
    "Employees": "employees",
    "Emp. ID": "emp_id",
    "Emp ID": "emp_id",
    "EMP NO": "emp_id",
    "Employee ID": "emp_id",
    "emp.id": "emp_id",

    "Name (Arabic)": "name_ar",
    "Name Arabic": "name_ar",
    "Name": "name_ar",
    "name.(arabic)": "name_ar",

    "Name (English)": "name_en",
    "Name English": "name_en",
    "name.(english)": "name_en",

    "Passport No.": "passport_no",
    "Passport No": "passport_no",
    "passport.no": "passport_no",

    "Nationality": "nationality",

    "Profession": "profession",
    "Actual Profession": "profession",
    "profession": "profession",

    "Sponsor Name": "sponsor",
    "Spensor": "sponsor",
    "Spensor Name": "sponsor",
    "sponsor": "sponsor",

    "Evaliuation": "evaluation",  # <-- تم التعديل هنا
    "Evaluation": "evaluation",   # <-- يفضل إبقاء الاثنين للاحتياط

    # Arabic headers
    "الرقم الوظيفي": "emp_id",
    "الاسم عربي": "name_ar",
    "الاسم انجليزي": "name_en",
    "رقم الجواز": "passport_no",
    "الجنسية": "nationality",
    "المهنة": "profession",
    "اسم الكفيل": "sponsor",
    "Sponsor": "sponsor",
    "sponsor": "sponsor",    # أضف هذا السطر
}


INVISIBLE_CHARS = {"\u200f", "\ufeff"}


def _clean_header(name: str) -> str:
    """Normalize Excel column headers by stripping extras."""
    name = str(name)
    for ch in INVISIBLE_CHARS:
        name = name.replace(ch, "")
    name = name.strip()
    name = re.sub(r"[:\u0589\u061b]+$", "", name).strip()
    name = re.sub(r"\.\d+$", "", name)
    return name

# ------------------------------------------------------------------------------
# صفحات عامة
# ------------------------------------------------------------------------------

def home(request):
    learner = Learner.objects.filter(user=request.user).first() if request.user.is_authenticated else None
    return render(request, "core/home.html", {"learner": learner})


def recruitment_dashboard(request):
    return render(request, "core/recruitment_dashboard.html")


def recruitment_placeholder(request, page):
    return render(request, "core/recruitment_placeholder.html", {"page": page})

# ------------------------------------------------------------------------------
# التسجيل / التفعيل / تسجيل الدخول
# ------------------------------------------------------------------------------

def _validate_registration(data) -> list[str]:
    errs: list[str] = []
    required = {
        "first_name_ar": "الاسم الأول (عربي)",
        "last_name_ar":  "اسم العائلة (عربي)",
        "first_name_en": "First Name (English)",
        "last_name_en":  "Last Name (English)",
        "employee_number": "الرقم الوظيفي",
        "department": "الإدارة",
        "section": "القسم",
        "email": "البريد الإلكتروني",
        "password": "كلمة المرور",
        "confirm_password": "تأكيد كلمة المرور",
    }
    for f, lbl in required.items():
        if not data.get(f):
            errs.append(f"حقل «{lbl}» مطلوب")

    if data.get("email") and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", data["email"]):
        errs.append("صيغة البريد الإلكتروني غير صحيحة")
    if data.get("national_id") and not re.fullmatch(r"\d{10}", data["national_id"]):
        errs.append("رقم الهوية يجب أن يتكوّن من 10 أرقام")
    if data.get("password") != data.get("confirm_password"):
        errs.append("كلمة المرور غير متطابقة")
    if User.objects.filter(username=data.get("email")).exists():
        errs.append("هذا البريد الإلكتروني مستخدم بالفعل")
    return errs


def register(request):
    if request.method != "POST":
        return render(request, "core/register.html")

    errors = _validate_registration(request.POST)
    if errors:
        for e in errors:  # type: ignore
            messages.error(request, e)
        return render(request, "core/register.html")

    d = request.POST
    user = User.objects.create_user(
        username=d["email"],
        email=d["email"],
        password=d["password"],
        is_active=False,
    )

    dept, _ = Department.objects.get_or_create(name=d["department"].strip())
    sect = Section.objects.get_or_create(name=d["section"].strip(), department=dept)[0]
    nat    = Nationality.objects.get_or_create(name=d["nationality"].strip())[0] if d.get("nationality") else None
    sector = Sector.objects.get_or_create(name=d["sector"].strip())[0]       if d.get("sector") else None

    Learner.objects.create(
        first_name_ar=d["first_name_ar"],
        last_name_ar=d["last_name_ar"],
        first_name_en=d["first_name_en"],
        last_name_en=d["last_name_en"],
        employee_number=d["employee_number"],
        department=dept,
        section=sect,
        manager=d.get("manager", ""),
        email=d["email"],
        mobile=d.get("mobile", ""),
        national_id=d.get("national_id", ""),
        nationality=nat,
        sector=sector,
        user=user,
    )

    site  = get_current_site(request)
    uid   = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    link  = f"http://{site.domain}{reverse('core:activate', args=[uid, token])}"
    user.email_user("تفعيل الحساب", f"مرحباً،\nلإتمام التسجيل اضغط الرابط:\n{link}")

    messages.success(request, "تم إنشاء الحساب بنجاح. تفقد بريدك الإلكتروني للتفعيل.")
    return redirect("core:register_thanks")


def register_thanks(request):
    return render(request, "core/register_thanks.html")


def activate(request, uidb64, token):
    try:
        uid  = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "تم تفعيل الحساب، بإمكانك تسجيل الدخول.")
        return redirect("core:login")
    return render(request, "core/activation_invalid.html", status=400)


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("core:home")
    if form.errors:
        messages.error(request, "اسم المستخدم أو كلمة المرور غير صحيحة")
    return render(request, "core/login.html", {"form": form})

# ------------------------------------------------------------------------------
# صفحات الخدمات
# ------------------------------------------------------------------------------

def service_page(request, service: str):
    if service == "my_works":
        return render(request, "core/my_works.html")

    names = {
        "needs_analysis":      "تحليل الاحتياجات التدريبية",
        "share_knowledge":     "شاركنا المعرفة",
        "youtube_tracks":      "مسارات دورات اليوتيوب",
        "skills_program":      "برنامج مهارات",
        "articles":            "مقالات",
        "my_certificates":     "شهاداتي",
        "course_announcements":"إعلانات الدورات التدريبية",
        "my_works":            "أعمالي",
    }
    return render(request, "core/service_page.html", {"service_name": names.get(service, service)})


def other_services(request):
    return render(request, "core/other_services.html")

# ------------------------------------------------------------------------------
# أدوات مساعدة (إكسل)
# ------------------------------------------------------------------------------

def _extract_employee_data(row: dict) -> dict:
    """Return cleaned values from a raw Excel row."""
    cleaned: dict[str, object] = {}
    for k, v in row.items():
        name = _clean_header(k)
        if name in cleaned:
            current = cleaned[name]
            if (current in ("", None)) and (v not in ("", None)):
                cleaned[name] = v
        else:
            cleaned[name] = v
    data: dict[str, object] = {}
    for field, aliases in EMPLOYEE_COLUMN_MAP.items():
        for a in aliases:
            if a in cleaned and cleaned[a] not in ("", None):
                val = cleaned[a]
                if field == "start_date":
                    try:
                        val = pd.to_datetime(val).date()
                    except Exception:
                        val = None
                elif field == "evaluation":
                    try:
                        val = Decimal(str(val))
                    except Exception:
                        val = None
                data[field] = val
                break

    serial = str(data.get("serial", "")).strip()
    if serial.isdigit():
        data["serial"] = int(serial)
    else:
        data.pop("serial", None)
    return data

# ------------------------------------------------------------------------------
# رفع كشوف الاستقدام
# ------------------------------------------------------------------------------

def upload_employees(request):
    if request.method == "POST":
        form = RecruitmentReportForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, form.errors.as_text())
            return redirect("core:upload_employees")

        report_date = form.cleaned_data["report_date"]
        is_haramain = form.cleaned_data["is_haramain"] == "true"

        saved, skipped, errors = 0, [], []

        for excel in request.FILES.getlist("file"):
            if RecruitmentReport.objects.filter(filename=excel.name, report_date=report_date, is_haramain=is_haramain).exists():
                skipped.append(excel.name)
                continue

            try:
                df = pd.read_excel(excel)
            except Exception as exc:
                logger.exception("Failed reading %s", excel.name)
                errors.append(f"{excel.name}: {exc}")
                continue

            report = RecruitmentReport.objects.create(
                filename   = excel.name,
                uploaded_by= request.user if request.user.is_authenticated else None,
                report_date= report_date,
                file_size  = excel.size,
                is_haramain= is_haramain,
                columns    = list(df.columns),
                rows       = df.fillna("").to_dict(orient="records"),
            )

            added = 0
            for r in report.rows:
                data = _extract_employee_data({k.strip(): v for k, v in r.items()})
                if not data:
                    continue
                emp_no = str(data.pop("employee_number", "")).strip()
                if not emp_no:
                    continue
                defaults = {k: v for k, v in data.items() if v is not None}
                defaults.update({"report": report, "is_haramain": is_haramain})
                RecruitmentEmployee.objects.update_or_create(
                    employee_number=emp_no,
                    defaults=defaults,
                )
                added += 1

            saved += bool(added)
            if not added:
                errors.append(f"{excel.name}: لا توجد بيانات موظفين")

        if saved:
            messages.success(request, f"تم حفظ {saved} كشف بنجاح")
        if skipped:
            messages.warning(request, "تم تخطي الملفات المكررة: " + ", ".join(skipped))
        if errors:
            messages.error(request, "أخطاء: " + "; ".join(errors))
        return redirect("core:upload_employees")

    # ---------- GET ----------
    form = RecruitmentReportForm()
    filter_type = request.GET.get("type")
    year, month, search = request.GET.get("year"), request.GET.get("month"), request.GET.get("q")

    qs = RecruitmentReport.objects.all()
    if filter_type in ("true", "false"):
        qs = qs.filter(is_haramain=(filter_type == "true"))
    if year:
        qs = qs.filter(report_date__year=year)
    if month:
        qs = qs.filter(report_date__month=month)
    if search:
        qs = qs.filter(filename__icontains=search)

    qs = qs.order_by("-report_date")
    grouped: dict[int, dict[int, dict[int, list[RecruitmentReport]]]] = {}
    for rep in qs:
        d = rep.report_date
        grouped.setdefault(d.year, {}).setdefault(d.month, {}).setdefault(d.day, []).append(rep)

    stats = {
        "total_reports": qs.count(),
        "total_employees": sum(len(r.rows) for r in qs),
        "latest": qs.first(),
    }

    return render(request, "core/upload_employees.html", {
        "form": form,
        "reports": grouped,
        "reports_list": qs,
        "filter_type": filter_type,
        "stats": stats,
        "year": year,
        "month": month,
        "search": search,
    })


def upload_legacy_records(request):
    """Upload legacy employee spreadsheets to LegacyRecruitmentRecord."""

    if request.method == "POST":
        form = LegacyUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, form.errors.as_text())
            return redirect("core:upload_legacy_records")

        existing_ids = set(
            LegacyRecruitmentRecord.objects.values_list("emp_id", flat=True)
        )
        added_total = 0

        for excel in request.FILES.getlist("file"):
            try:
                df = pd.read_excel(excel)
            except Exception as exc:
                logger.exception("Failed reading %s", excel.name)
                messages.error(request, f"{excel.name}: {exc}")
                continue

            df.columns = [_clean_header(c) for c in df.columns]
            df.rename(columns=LEGACY_COLUMN_MAP, inplace=True)

            sponsor_indices = [i for i, c in enumerate(df.columns) if c == "sponsor"]

            for _, row in df.iterrows():
                emp_id = clean_emp_id(row.get("emp_id", ""))
                if not emp_id or emp_id in existing_ids:
                    continue
                existing_ids.add(emp_id)

                sponsor_value = None
                for idx in sponsor_indices:
                    if idx < len(row):
                        val = row.iloc[idx]
                        if val not in ("", None) and not (isinstance(val, float) and pd.isna(val)):
                            sponsor_value = val
                            break

                LegacyRecruitmentRecord.objects.create(
                    employees=str(row.get("employees", "")).strip() or None,
                    emp_id=emp_id,
                    name_ar=(str(row.get("name_ar", "")).strip() or None),
                    name_en=(str(row.get("name_en", "")).strip() or None),
                    passport_no=(str(row.get("passport_no", "")).strip() or None),
                    nationality=(str(row.get("nationality", "")).strip() or None),
                    profession=(str(row.get("profession", "")).strip() or None),
                    sponsor=(str(sponsor_value).strip() if sponsor_value not in (None, "") else None),
                )
                added_total += 1

        if added_total:
            messages.success(request, f"تمت إضافة {added_total} سجلًا بنجاح")
        else:
            messages.info(request, "لا توجد سجلات مضافة")
        return redirect("core:upload_legacy_records")

    form = LegacyUploadForm()
    records = LegacyRecruitmentRecord.objects.order_by("-id")[:50]
    return render(request, "core/upload_legacy_records.html", {"form": form, "records": records})

# ------------------------------------------------------------------------------
# مشاهد التقارير / الموظفين
# ------------------------------------------------------------------------------

def report_detail(request, pk):
    return render(request, "core/report_detail.html", {"report": RecruitmentReport.objects.get(pk=pk)})


@require_POST
def delete_report(request, pk):
    RecruitmentReport.objects.filter(pk=pk).delete()
    messages.success(request, "تم حذف الكشف")
    return redirect("core:upload_employees")


def export_report_excel(request, pk):
    rep = RecruitmentReport.objects.get(pk=pk)
    df  = pd.DataFrame(rep.rows, columns=rep.columns)

    # Remove completely empty rows before exporting
    df = df.dropna(how="all")
    df = df[~(df == "").all(axis=1)]
    resp = HttpResponse(content_type="application/vnd.ms-excel")
    resp["Content-Disposition"] = f'attachment; filename="{rep.filename}"'
    df.to_excel(resp, index=False)
    return resp


def edit_report(request, pk):
    rep = RecruitmentReport.objects.get(pk=pk)
    form = RecruitmentReportEditForm(request.POST or None, instance=rep)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تم تحديث الكشف")
        return redirect("core:upload_employees")
    return render(request, "core/edit_report.html", {"form": form, "report": rep})


import re

def clean_emp_id(val):
    """
    Extract only the digits from emp_id field to ensure a clean employee number.
    """
    if isinstance(val, str):
        m = re.search(r"\d+", val)
        return m.group(0) if m else val
    elif isinstance(val, int):
        return str(val)
    elif hasattr(val, "__str__"):
        m = re.search(r"\d+", str(val))
        return m.group(0) if m else str(val)
    return str(val)

from django.db.models import Max

@require_POST
def import_report_records(request, pk):
    """Import selected report rows into LegacyRecruitmentRecord."""
    report = RecruitmentReport.objects.get(pk=pk)

    df = pd.DataFrame(report.rows)
    df.columns = [_clean_header(c) for c in df.columns]
    df.rename(columns=LEGACY_COLUMN_MAP, inplace=True)
    print("\U0001fa84 columns:", df.columns.tolist())

    sponsor_indices = [i for i, col in enumerate(df.columns) if col == "sponsor"]

    existing_ids = set(
        LegacyRecruitmentRecord.objects.values_list("emp_id", flat=True)
    )

    # جلب آخر رقم تسلسلي موجود في قاعدة البيانات، لو ما فيه سجلات يبدأ من 0
    last_serial = LegacyRecruitmentRecord.objects.aggregate(
        max_serial=Max("employees")
    )["max_serial"] or 0

    added = 0
    for _, row in df.iterrows():
        emp_id = clean_emp_id(row.get("emp_id", ""))
        if not emp_id or emp_id in existing_ids:
            continue
        existing_ids.add(emp_id)

        sponsor_value = None
        for idx in sponsor_indices:
            if idx < len(row):
                val = row.iloc[idx]
                if val not in ("", None) and not (isinstance(val, float) and pd.isna(val)):
                    sponsor_value = val
                    break

        name_ar = (row.get("name_ar") or row.get("name") or "").strip() or None
        name_en = (row.get("name_en") or "").strip() or None
        profession = (row.get("profession") or row.get("official_job") or "").strip() or None

        if not name_ar and not name_en:
            # Skip completely blank rows
            continue

        missing = [k for k in ["name_ar", "name_en", "profession"] if not row.get(k)]
        if missing:
            # تم تعديل السطر التالي لتحويل emp_id لنص
            print("\u26a0\ufe0f MISSING:", missing, "for", str(emp_id))

        # زيادة الرقم التسلسلي
        last_serial += 1

        LegacyRecruitmentRecord.objects.create(
            employees=last_serial,  # الرقم التسلسلي الجديد
            emp_id=emp_id,
            name_ar=name_ar,
            name_en=name_en,
            passport_no=(str(row.get("passport_no", "")).strip() or None),
            nationality=(str(row.get("nationality", "")).strip() or None),
            profession=profession,
            sponsor=(str(sponsor_value).strip() if sponsor_value not in (None, "") else None),

            # الإضافات المطلوبة:
            date=report.report_date,
            month=report.report_date.strftime("%b"),         # مثال: Jan أو Feb
            month_number=report.report_date.month,           # مثال: 1 أو 2
            sector="حرمين" if report.is_haramain else "غير حرمين",
            year=report.report_date.year,
        )

        added += 1

    if added:
        messages.success(request, f"تم إضافة {added} سجل بنجاح")
    else:
        messages.info(request, "لا توجد سجلات جديدة لإضافتها")
    return redirect("core:upload_employees")


# ------------------------------------------------------------------------------
# تقييم فردي سريع
# ------------------------------------------------------------------------------

def evaluate_employee(request, pk):
    emp  = RecruitmentEmployee.objects.get(pk=pk)
    form = EmployeeEvaluationForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        ev = form.save(commit=False)
        ev.employee   = emp
        ev.evaluator  = request.user if request.user.is_authenticated else None
        ev.is_haramain = emp.is_haramain
        ev.save()
        messages.success(request, "تم حفظ التقييم")
        return redirect("core:evaluate_employee", pk=emp.pk)
    return render(request, "core/evaluate_employee.html", {"form": form, "employee": emp})


@require_POST
def set_final_score(request, pk):
    emp = RecruitmentEmployee.objects.get(pk=pk)
    try:
        emp.final_score = Decimal(request.POST.get("final_score"))
        emp.save()
    except Exception:
        pass
    return redirect("core:upload_employees")

# ------------------------------------------------------------------------------
# تحويل الدرجة الرقمية → الحرف والتوقعات
# ------------------------------------------------------------------------------

def _grade_mapping(score: Decimal) -> tuple[str, str]:
    s = float(score)
    if 85 <= s <= 100:
        return "A", "Exceeds Expectations"
    if 75 <= s <= 84:
        return "B", "Meets Expectations"
    if 60 <= s <= 74:
        return "C", "Satisfactory"
    return "F", "Does not meet expectations"

# ------------------------------------------------------------------------------
# إدخال نتائج التقييم دفعة واحدة
# ------------------------------------------------------------------------------

def input_evaluation_results(request):
    # قائمة التواريخ
    dates: dict[int, dict[int, set[int]]] = {}
    for rep in RecruitmentReport.objects.all():
        d = rep.report_date
        dates.setdefault(d.year, {}).setdefault(d.month, set()).add(d.day)

    year, month, day = request.GET.get("year"), request.GET.get("month"), request.GET.get("day")
    selected: list[RecruitmentEmployee] = []

    def _sel(d: datetime.date) -> list[RecruitmentEmployee]:
        return list(RecruitmentEmployee.objects.filter(report__report_date=d).order_by("serial", "id"))

    # ---------- POST (حفظ) ----------
    if request.method == "POST":
        year, month, day = request.POST["year"], request.POST["month"], request.POST["day"]
        try:
            date_obj = datetime.date(int(year), int(month), int(day))
            selected = _sel(date_obj)
        except Exception:
            selected = []

        for emp in selected:
            raw_score  = request.POST.get(f"score_{emp.id}", "").strip()
            raw_result = request.POST.get(f"result_{emp.id}", "").strip()
            raw_expect = request.POST.get(f"result_expectations_{emp.id}", "").strip()
            raw_date   = request.POST.get(f"date_{emp.id}", "").strip()
            changed = False

            # Absent
            if raw_score.lower() == "absent":
                emp.final_score = None
                emp.result = emp.result_expectations = "Absent"
                changed = True
            elif raw_score:
                try:
                    dec = Decimal(raw_score)
                    emp.final_score = dec
                    emp.result, emp.result_expectations = _grade_mapping(dec)
                    changed = True
                except Exception:
                    pass

            # يدوي
            if raw_result:
                emp.result = raw_result; changed = True
            if raw_expect:
                emp.result_expectations = raw_expect; changed = True

            # التاريخ
            if raw_date:
                try:
                    emp.evaluation_date = datetime.date.fromisoformat(raw_date)
                    changed = True
                except ValueError:
                    pass
            elif emp.evaluation_date is None:
                # افتراضيًا اجعل التاريخ مطابقًا لتاريخ التقرير
                emp.evaluation_date = emp.report.report_date
                changed = True

            if changed:
                emp.save()

        messages.success(request, "تم حفظ الدرجات")
        return redirect(f"{reverse('core:input_evaluation_results')}?year={year}&month={month}&day={day}")

    # ---------- GET ----------
    elif year and month and day and year.isdigit() and month.isdigit() and day.isdigit():
        try:
            selected = _sel(datetime.date(int(year), int(month), int(day)))
        except Exception:
            selected = []

    years = sorted(dates.keys(), reverse=True)
    months = (
        sorted(dates.get(int(year), {}).keys(), reverse=True)
        if year and year.isdigit()
        else []
    )
    days = (
        sorted(dates.get(int(year), {}).get(int(month), []), reverse=True)
        if year and month and year.isdigit() and month.isdigit()
        else []
    )

    context = {
        "years": years,
        "months": months,
        "days": days,
        "selected_year": year,
        "selected_month": month,
        "selected_day": day,
        "employees": selected,
        "reports": RecruitmentReport.objects.filter(
            report_date=datetime.date(int(year), int(month), int(day))
        )
        if (
            year and month and day and year.isdigit() and month.isdigit() and day.isdigit()
        )
        else [],
        "date_selectors": [
            ("year", years, year),
            ("month", months, month),
            ("day", days, day),
        ],
    }
    return render(request, "core/input_results.html", context)

# ------------------------------------------------------------------------------
# شجرة الفلترة و JSON
# ------------------------------------------------------------------------------

def tree_filter_page(request):
    return render(request, "core/tree_filter.html")


def tree_filter_data(request):
    grouped: dict[int, dict[int, set[int]]] = {}
    for rep in RecruitmentReport.objects.all():
        d = rep.report_date
        grouped.setdefault(d.year, {}).setdefault(d.month, set()).add(d.day)

    res: list[dict] = []
    for y in sorted(grouped.keys(), reverse=True):
        res.append({"id": str(y), "parent": "#", "text": str(y)})
        for m in sorted(grouped[y], reverse=True):
            mid = f"{y}-{m:02d}"
            res.append({"id": mid, "parent": str(y), "text": calendar.month_name[m]})
            for d in sorted(grouped[y][m], reverse=True):
                res.append({"id": f"{mid}-{d:02d}", "parent": mid, "text": f"{d:02d}"})
    return JsonResponse(res, safe=False)


def tree_filter_results(request):
    sel = request.GET.getlist("selected[]")
    qs  = RecruitmentReport.objects.all()
    if sel:
        q = Q()
        for node in sel:
            p = node.split("-")
            if len(p) == 1:
                q |= Q(report_date__year=int(p[0]))
            elif len(p) == 2:
                q |= Q(report_date__year=int(p[0]), report_date__month=int(p[1]))
            elif len(p) == 3:
                q |= Q(report_date__year=int(p[0]), report_date__month=int(p[1]), report_date__day=int(p[2]))
        qs = qs.filter(q)
    return JsonResponse([
        {"id": r.id, "filename": r.filename, "report_date": r.report_date.isoformat(), "is_haramain": r.is_haramain}
        for r in qs.order_by("-report_date")
    ], safe=False)

# ------------------------------------------------------------------------------
# API بسيطة للكشوف (JSON)
# ------------------------------------------------------------------------------

def reports_json(request):
    qs = RecruitmentReport.objects.all()
    if q := request.GET.get("q"):
        qs = qs.filter(filename__icontains=q)
    if t := request.GET.get("type") in ("true", "false"):
        qs = qs.filter(is_haramain=(t == "true"))
    if start := request.GET.get("start"):
        qs = qs.filter(report_date__gte=start)
    if end := request.GET.get("end"):
        qs = qs.filter(report_date__lte=end)

    qs = qs.order_by("-uploaded_at")
    return JsonResponse([
        {
            "id": r.id,
            "filename": r.filename,
            "uploaded_at": r.uploaded_at.strftime("%Y-%m-%d %H:%M"),
            "file_size_formatted": filesizeformat(r.file_size),
            "is_haramain": r.is_haramain,
            "report_date": r.report_date.isoformat(),
        } for r in qs
    ], safe=False)


@require_http_methods(["GET", "POST"])
def update_database(request):
    """Export all legacy recruitment records to an Excel file."""
    if request.method == "POST":
        # 1) Fetch all records from the legacy table using explicit field names
        field_map = {
            "employees": "Employees",
            "emp_id": "Emp. ID",
            "evaluation": "Evaliuation",
            "result": "Result",
            "result_expectations": "Result Expectations",
            "name_ar": "Name (Arabic)",
            "name_en": "Name (English)",
            "passport_no": "Passport No.",
            "nationality": "Nationality",
            "profession": "Profession",
            "profession_group": "Profession Group",
            "sponsor": "Sponsor",
            "date": "Date",
            "month": "Month",
            "month_number": "Month Number",
            "sector": "Sector",
            "team_group": "Team Group",
            "project": "Project",
            "management": "Management",
            "project_manager": "Project Manager",
            "director_of_management": "Director of Management",
            "year": "Year",
        }

        qs = LegacyRecruitmentRecord.objects.all()
        data = list(qs.values(*field_map.keys()))
        df = pd.DataFrame.from_records(data, columns=field_map.keys())

        # Remove completely empty rows before exporting
        df = df.dropna(how="all")
        df = df[~(df == "").all(axis=1)]

        # 2) Rename columns to match the expected export headers
        df.rename(columns=field_map, inplace=True)

        # 3) Ensure all final columns exist and are ordered correctly
        RECRUITMENT_COLUMNS = list(field_map.values())
        for col in RECRUITMENT_COLUMNS:
            if col not in df.columns:
                df[col] = ""

        df = df[RECRUITMENT_COLUMNS]

        # 4) Remove timezone from any datetime columns
        for col in df.columns:
            if pd.api.types.is_datetime64tz_dtype(df[col]):
                df[col] = df[col].dt.tz_localize(None)

        # 5) Prepare the Excel response
        today = datetime.date.today().strftime("%Y%m%d")
        filename = f"recruitment_placeholder_{today}.xlsx"
        resp = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        resp["Content-Disposition"] = f"attachment; filename={filename}"

        df.to_excel(resp, index=False)
        return resp

    return render(request, "core/update_db.html")
