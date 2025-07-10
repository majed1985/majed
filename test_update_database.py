import io
import pandas as pd
import datetime
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from core.models import RecruitmentEmployee

class UpdateDatabaseTimezoneTest(TestCase):
    def test_export_removes_timezone(self):
        RecruitmentEmployee.objects.create(
            serial=1, employee_number="10", name="Ali"
        )

        url = reverse("core:update_database")
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)

        buf = io.BytesIO(resp.content)
        df = pd.read_excel(buf)

        self.assertIn("created at", df.columns)
        value = df.loc[0, "created at"]
        self.assertFalse(hasattr(value, 'tzinfo') and value.tzinfo)
