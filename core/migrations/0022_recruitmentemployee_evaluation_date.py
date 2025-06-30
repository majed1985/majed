from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0021_recruitmentemployee_report"),
    ]

    operations = [
        migrations.AddField(
            model_name="recruitmentemployee",
            name="evaluation_date",
            field=models.DateField(
                verbose_name="تاريخ آخر تقييم", null=True, blank=True
            ),
        ),
    ]
