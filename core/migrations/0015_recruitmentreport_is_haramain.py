from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("core", "0014_update_recruitmentemployee"),
    ]

    operations = [
        migrations.AddField(
            model_name="recruitmentreport",
            name="is_haramain",
            field=models.BooleanField(default=False, verbose_name="حرمين"),
        ),
        migrations.AlterUniqueTogether(
            name="recruitmentreport",
            unique_together={("filename", "report_date", "is_haramain")},
        ),
    ]
