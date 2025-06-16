from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "core"

urlpatterns = [
    # ✅ الصفحة الرئيسية
    path("", views.home, name="home"),

    # ✅ صفحات التسجيل
    path("register/", views.register, name="register"),
    path("register/thanks/", views.register_thanks, name="register_thanks"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),

    # ✅ تسجيل الدخول
    path("login/", views.login_view, name="login"),

    # ✅ تسجيل الخروج
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="core:home"),
        name="logout",
    ),

    # ✅ دورة إعادة تعيين كلمة المرور
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="core/password_reset.html"
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="core/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="core/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="core/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
