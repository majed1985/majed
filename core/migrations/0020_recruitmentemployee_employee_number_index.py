from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_recruitmentemployee_decimal_scores'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recruitmentemployee',
            name='employee_number',
            field=models.CharField(max_length=50, verbose_name='الرقم الوظيفي', db_index=True),
        ),
    ]
