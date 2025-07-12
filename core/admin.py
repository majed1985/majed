# core/admin.py
from django.contrib import admin

# The Learner model is intentionally not registered with the Django admin
# interface. Administrators manage trainees through custom views instead of
# using the default admin site.
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
