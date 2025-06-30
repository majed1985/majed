from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0020_recruitmentemployee_employee_number_index"),
    ]

    operations = [
        migrations.AddField(
            model_name="recruitmentemployee",
            name="report",
            field=models.ForeignKey(
                to="core.recruitmentreport",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="employees",
                verbose_name="الكشف",
                null=True,
                blank=True,
            ),
        ),
    ]
