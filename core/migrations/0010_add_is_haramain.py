from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_recruitment_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='recruitmentemployee',
            name='is_haramain',
            field=models.BooleanField(default=False, verbose_name='حرمين'),
        ),
        migrations.AddField(
            model_name='employeeevaluation',
            name='is_haramain',
            field=models.BooleanField(default=False, verbose_name='حرمين'),
        ),
    ]
