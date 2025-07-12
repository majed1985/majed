from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "core"

urlpatterns = [
    # ✅ الصفحة الرئيسية
    path("", views.home, name="home"),
    path("recruitment/", views.recruitment_dashboard, name="recruitment_dashboard"),
    path("recruitment/step/<str:page>/", views.recruitment_placeholder, name="recruitment_step"),

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

    # ✅ صفحة الخدمات الأخرى وكروت الخدمات
    path("other-services/", views.other_services, name="other_services"),
    path("service/<str:service>/", views.service_page, name="service_page"),

    # استقدام الحديث
    path("recruitment/upload/", views.upload_employees, name="upload_employees"),
    path(
        "recruitment/upload-legacy/",
        views.upload_legacy_records,
        name="upload_legacy_records",
    ),
    path("recruitment/report/<int:pk>/", views.report_detail, name="report_detail"),
    path("recruitment/report/<int:pk>/delete/", views.delete_report, name="delete_report"),
    path("recruitment/report/<int:pk>/edit/", views.edit_report, name="edit_report"),
    path("recruitment/report/<int:pk>/export/", views.export_report_excel, name="export_report"),
    path("recruitment/report/<int:pk>/import/", views.import_report_records, name="import_report_records"),
    path("recruitment/reports/json/", views.reports_json, name="reports_json"),
    path("recruitment/<int:pk>/evaluate/", views.evaluate_employee, name="evaluate_employee"),
    path("recruitment/input-results/", views.input_evaluation_results, name="input_evaluation_results"),
    path("recruitment/<int:pk>/final-score/", views.set_final_score, name="set_final_score"),
    path("recruitment/update-db/", views.update_database, name="update_database"),

    # فلترة شجرية تجريبية
    path("tree-filter/", views.tree_filter_page, name="tree_filter"),
    path("tree-filter/data/", views.tree_filter_data, name="tree_filter_data"),
    path("tree-filter/results/", views.tree_filter_results, name="tree_filter_results"),
]
