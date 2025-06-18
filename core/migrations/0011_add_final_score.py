from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0010_add_is_haramain'),
    ]

    operations = [
        migrations.AddField(
            model_name='recruitmentemployee',
            name='final_score',
            field=models.FloatField(null=True, blank=True, verbose_name='الدرجة النهائية'),
        ),
    ]
