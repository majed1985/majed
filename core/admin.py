# core/admin.py
from django.contrib import admin

from .models import Learner


@admin.register(Learner)
class LearnerAdmin(admin.ModelAdmin):
    list_display = ("first_name_ar", "last_name_ar", "date_created")
    search_fields = (
        "first_name_ar",
        "last_name_ar",
        "first_name_en",
        "last_name_en",
    )


# The following models were previously registered with the admin site but have
# been removed as they are no longer managed through the Django admin
# interface:
# - Department
# - Section
# - Nationality
# - Sector
# - RecruitmentEmployee
# - EmployeeEvaluation
# - RecruitmentReport
# - LegacyRecruitmentRecord

