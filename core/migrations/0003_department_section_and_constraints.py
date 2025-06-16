from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_learner_department_learner_email_and_more"),
    ]

    operations = [
        # -------- 1) Department ---------------------------------------------
        migrations.CreateModel(
            name="Department",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        "الإدارة",
                        max_length=50,
                        unique=True,
                    ),
                ),
            ],
        ),

        # -------- 2) Section -------------------------------------------------
        migrations.CreateModel(
            name="Section",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        "القسم",
                        max_length=50,
                    ),
                ),
                (
                    "department",
                    models.ForeignKey(
                        "core.Department",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sections",
                        verbose_name="الإدارة",
                    ),
                ),
            ],
            options={
                "unique_together": {("department", "name")},
            },
        ),

        # -------- 3) تعديل حقول Learner -------------------------------------
        migrations.AlterField(
            model_name="learner",
            name="department",
            field=models.ForeignKey(
                "core.Department",
                on_delete=django.db.models.deletion.SET_NULL,
                null=True,
                blank=True,
                verbose_name="الإدارة",
            ),
        ),
        migrations.AlterField(
            model_name="learner",
            name="section",
            field=models.ForeignKey(
                "core.Section",
                on_delete=django.db.models.deletion.SET_NULL,
                null=True,
                blank=True,
                verbose_name="القسم",
            ),
        ),
        migrations.AlterField(
            model_name="learner",
            name="employee_number",
            field=models.CharField(
                "الرقم الوظيفي",
                max_length=20,
                unique=True,
                null=True,
                blank=True,
                db_index=True,
            ),
        ),
        migrations.AlterField(
            model_name="learner",
            name="email",
            field=models.EmailField(
                "البريد الإلكتروني",
                unique=True,
                null=True,
                blank=True,
                db_index=True,
                max_length=254,
            ),
        ),
        migrations.AlterField(
            model_name="learner",
            name="national_id",
            field=models.CharField(
                "رقم الهوية",
                max_length=20,
                unique=True,
                null=True,
                blank=True,
                db_index=True,
            ),
        ),
    ]
