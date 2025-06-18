from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0013_merge_20250618_1429"),
    ]

    operations = [
        migrations.AddField(
            model_name="recruitmentemployee",
            name="serial",
            field=models.PositiveIntegerField(null=True, blank=True, verbose_name="التسلسل"),
        ),
        migrations.AddField(
            model_name="recruitmentemployee",
            name="employee_number",
            field=models.CharField(default="", max_length=50, verbose_name="الرقم الوظيفي"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="recruitmentemployee",
            name="name_en",
            field=models.CharField(max_length=100, blank=True, null=True, verbose_name="الاسم انجليزي"),
        ),
        migrations.AddField(
            model_name="recruitmentemployee",
            name="passport_number",
            field=models.CharField(max_length=100, blank=True, null=True, verbose_name="رقم الجواز"),
        ),
        migrations.AddField(
            model_name="recruitmentemployee",
            name="sponsor_name",
            field=models.CharField(max_length=100, blank=True, null=True, verbose_name="اسم الكفيل"),
        ),
        migrations.AddField(
            model_name="recruitmentemployee",
            name="evaluation",
            field=models.FloatField(null=True, blank=True, verbose_name="Evaluation"),
        ),
        migrations.AddField(
            model_name="recruitmentemployee",
            name="result",
            field=models.CharField(max_length=100, blank=True, null=True, verbose_name="Result"),
        ),
        migrations.AddField(
            model_name="recruitmentemployee",
            name="result_expectations",
            field=models.CharField(max_length=100, blank=True, null=True, verbose_name="Result Expectations"),
        ),
        migrations.AlterField(
            model_name="recruitmentemployee",
            name="nationality",
            field=models.CharField(max_length=50, blank=True, null=True, verbose_name="الجنسية"),
        ),
        migrations.AlterField(
            model_name="recruitmentemployee",
            name="official_job",
            field=models.CharField(max_length=100, blank=True, null=True, verbose_name="المهنة"),
        ),
        migrations.AlterField(
            model_name="recruitmentemployee",
            name="start_date",
            field=models.DateField(blank=True, null=True, verbose_name="تاريخ المباشرة"),
        ),
        migrations.RemoveField(
            model_name="recruitmentemployee",
            name="actual_job",
        ),
        migrations.RemoveField(
            model_name="recruitmentemployee",
            name="computer_number",
        ),
        migrations.RemoveField(
            model_name="recruitmentemployee",
            name="project_name",
        ),
    ]
