from django.contrib import admin
from .models import RecruitmentReport

# إظهار فقط كشوف الاستقدام في لوحة الأدمن
admin.site.register(RecruitmentReport)
