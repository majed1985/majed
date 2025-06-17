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

from .models import Learner, Nationality, Sector


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

        # ----- حقل الإدارة والقسم نصياً --------------------------------------
        dept_name = data.get("department", "").strip()
        sect_name = data.get("section", "").strip()
        nat_name  = data.get("nationality", "").strip()
        sectr_name= data.get("sector", "").strip()

        department = dept_name or None
        section    = sect_name or None
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
