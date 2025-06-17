from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0007_department_section_charfields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='learner',
            name='department',
            field=models.ForeignKey(
                to='core.department',
                on_delete=django.db.models.deletion.SET_NULL,
                null=True,
                blank=True,
                verbose_name='الإدارة',
            ),
        ),
        migrations.AlterField(
            model_name='learner',
            name='section',
            field=models.ForeignKey(
                to='core.section',
                on_delete=django.db.models.deletion.SET_NULL,
                null=True,
                blank=True,
                verbose_name='القسم',
            ),
        ),
    ]
