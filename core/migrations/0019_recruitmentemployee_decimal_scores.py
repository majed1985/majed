from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_recruitmentreport_file_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recruitmentemployee',
            name='evaluation',
            field=models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Evaluation'),
        ),
        migrations.AlterField(
            model_name='recruitmentemployee',
            name='final_score',
            field=models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='الدرجة النهائية'),
        ),
    ]
