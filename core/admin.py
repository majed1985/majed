<<<<<<< HEAD
# core/admin.py
from django.contrib import admin

from .models import Learner, Department, Section, Nationality, Sector


@admin.register(Learner)
class LearnerAdmin(admin.ModelAdmin):
    list_display = ("first_name_ar", "last_name_ar", "date_created")
    search_fields = (
        "first_name_ar",
        "last_name_ar",
        "first_name_en",
        "last_name_en",
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("department", "name")
    list_filter = ("department",)
    search_fields = ("name",)


@admin.register(Nationality)
class NationalityAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
=======
# core/admin.py
from django.contrib import admin

from .models import Learner, Department, Section, Nationality, Sector


@admin.register(Learner)
class LearnerAdmin(admin.ModelAdmin):
    list_display = ("first_name_ar", "last_name_ar", "date_created")
    search_fields = (
        "first_name_ar",
        "last_name_ar",
        "first_name_en",
        "last_name_en",
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("department", "name")
    list_filter = ("department",)
    search_fields = ("name",)


@admin.register(Nationality)
class NationalityAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
>>>>>>> fefcbab3ba74fe1e50375ae2d8fb84f78fb632fe
