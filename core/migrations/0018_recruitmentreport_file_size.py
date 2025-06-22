from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_merge_20250620_2141'),
    ]

    operations = [
        migrations.AddField(
            model_name='recruitmentreport',
            name='file_size',
            field=models.PositiveIntegerField(default=0, verbose_name='حجم الملف (بايت)'),
        ),
    ]
