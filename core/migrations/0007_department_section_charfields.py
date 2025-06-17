from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_manager_charfield"),
    ]

    operations = [
        migrations.AlterField(
            model_name="learner",
            name="department",
            field=models.CharField(
                max_length=50,
                verbose_name="الإدارة",
                null=True,
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="learner",
            name="section",
            field=models.CharField(
                max_length=50,
                verbose_name="القسم",
                null=True,
                blank=True,
            ),
        ),
    ]
