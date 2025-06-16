<<<<<<< HEAD
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_department_section_and_constraints"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # جداول مرجعية جديدة
        migrations.CreateModel(
            name="Nationality",
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
                ("name", models.CharField("الجنسية", max_length=30, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Sector",
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
                ("name", models.CharField("القطاع", max_length=50, unique=True)),
            ],
        ),
        # حقل time-stamp لكل من Department / Section / Learner
        migrations.AddField(
            model_name="department",
            name="last_modified",
            field=models.DateTimeField(
                auto_now=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="section",
            name="last_modified",
            field=models.DateTimeField(
                auto_now=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="learner",
            name="last_modified",
            field=models.DateTimeField(
                auto_now=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        # تعديل علاقات Learner
        migrations.AlterField(
            model_name="learner",
            name="manager",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="managed_learners",
                to=settings.AUTH_USER_MODEL,
                verbose_name="المدير المباشر",
            ),
        ),
        migrations.AlterField(
            model_name="learner",
            name="nationality",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.nationality",
                verbose_name="الجنسية",
            ),
        ),
        migrations.AlterField(
            model_name="learner",
            name="sector",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.sector",
                verbose_name="القطاع",
            ),
        ),
    ]
=======
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_department_section_and_constraints"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # جداول مرجعية جديدة
        migrations.CreateModel(
            name="Nationality",
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
                ("name", models.CharField("الجنسية", max_length=30, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Sector",
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
                ("name", models.CharField("القطاع", max_length=50, unique=True)),
            ],
        ),
        # حقل time-stamp لكل من Department / Section / Learner
        migrations.AddField(
            model_name="department",
            name="last_modified",
            field=models.DateTimeField(
                auto_now=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="section",
            name="last_modified",
            field=models.DateTimeField(
                auto_now=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="learner",
            name="last_modified",
            field=models.DateTimeField(
                auto_now=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        # تعديل علاقات Learner
        migrations.AlterField(
            model_name="learner",
            name="manager",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="managed_learners",
                to=settings.AUTH_USER_MODEL,
                verbose_name="المدير المباشر",
            ),
        ),
        migrations.AlterField(
            model_name="learner",
            name="nationality",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.nationality",
                verbose_name="الجنسية",
            ),
        ),
        migrations.AlterField(
            model_name="learner",
            name="sector",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.sector",
                verbose_name="القطاع",
            ),
        ),
    ]
>>>>>>> fefcbab3ba74fe1e50375ae2d8fb84f78fb632fe
