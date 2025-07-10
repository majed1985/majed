import io
import pandas as pd
import datetime
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from core.models import LegacyRecruitmentRecord

class UpdateDatabaseTimezoneTest(TestCase):
    def test_export_removes_timezone(self):
        LegacyRecruitmentRecord.objects.create(
            employees="1",
            emp_id="10",
            date=timezone.now(),
        )

        url = reverse("core:update_database")
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)

        buf = io.BytesIO(resp.content)
        df = pd.read_excel(buf)

        self.assertIn("Date", df.columns)
        value = df.loc[0, "Date"]
        self.assertFalse(hasattr(value, 'tzinfo') and value.tzinfo)
